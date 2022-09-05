import os
import uuid
import json
import weakref
import importlib
import traceback
from pyrsistent import PClass, field


class Component:
    component_name = 'Base Component'


class Event(PClass):
    kind = field(type=str, mandatory=True)


class Entity:
    entity_index = {}
    component_index = {}

    def __init__(self):
        self.entity_id = str(uuid.uuid4())
        self.components = {}
        self.entity_index[self.entity_id] = self

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.entity_id}>"

    def attach(self, component:Component):
        self.components[component.component_name] = component
        if component.component_name not in self.component_index:
            self.component_index[component.component_name] = []
        self.component_index[component.component_name].append(self)

    @classmethod
    def with_component(cls, component_name):
        return cls.component_index.get(component_name, [])

    @classmethod
    def find(cls, entity_id):
        return cls.entity_index[entity_id]

    def __getitem__(self, attr):
        return self.components.get(attr)


class System:
    systems = {}
    subscriptions = {}

    def __init__(self):
        self.events = []
        self.systems[self.name] = self
        self.disabled = False
        module = importlib.import_module(name=self.__module__)
        self.loaded_at = os.path.getmtime(module.__file__)

    @property
    def name(self):
        return self.__class__.__name__

    def subscribe(self, event_kind):
        if event_kind not in self.subscriptions:
            self.subscriptions[event_kind] = []
        self.subscriptions[event_kind].append(self)

    @classmethod
    def inject(cls, event):
        for subscriber in cls.subscriptions.get(event.kind, []):
            subscriber.events.append(event)

    def reload(self):
        # Get a reference to the module containing the system
        module = importlib.import_module(name=self.__module__)
        last_modified = os.path.getmtime(module.__file__)

        if self.loaded_at >= last_modified:
            return

        # Reload the module that the system was defined in
        importlib.reload(module)

        # re-create the system
        cls = getattr(module, self.name)
        cls()

        print(f"Reloaded system {self.name}")

    def update(self):
        pass

    @classmethod
    def update_all(cls):
        for system_name, system in cls.systems.items():
            system.reload()
            if system.disabled:
                continue
            try:
                system.update()
            except SystemExit:
                # Exit exceptions should be allowed through
                raise
            except:
                # All other exceptions should disable the system until next reload
                traceback.print_exc()
                system.disabled = True


