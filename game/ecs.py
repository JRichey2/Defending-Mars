import os
import uuid
import importlib
import traceback


DELTA_TIME = 0.01667

NEXT_ENTITY = 1


class Entity:
    entity_index = {}
    component_index = {}
    pending_destruction = set()

    def __init__(self):
        global NEXT_ENTITY
        self.entity_id = NEXT_ENTITY
        NEXT_ENTITY += 1
        self.components = {}
        self.entity_index[self.entity_id] = self
        self.destroyed = False

    def __hash__(self):
        return hash(self.entity_id)

    def __eq__(self, other):
        return self.entity_id == other.entity_id

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.entity_id}>"

    def attach(self, component):
        self.components[component.component_name] = component
        if component.component_name not in self.component_index:
            self.component_index[component.component_name] = []
        self.component_index[component.component_name].append(self)

    @classmethod
    def with_component(cls, component_name):
        return cls.component_index.get(component_name, [])

    @classmethod
    def find(cls, entity_id):
        if entity_id not in cls.entity_index:
            return None
        else:
            return cls.entity_index[entity_id]

    def __getitem__(self, attr):
        return self.components.get(attr)

    def destroy(self):
        self.destroyed = True
        self.pending_destruction.add(self)

    @classmethod
    def clean_pending_destruction(cls):
        for component_name in cls.component_index:
            cls.component_index[component_name] = [
                e for e in cls.component_index[component_name]
                if e not in cls.pending_destruction
            ]
        cls.entity_index = {
            k: v for k, v in cls.entity_index.items()
            if k not in {e.entity_id for e in cls.pending_destruction}
        }


class System:
    systems = {}
    subscriptions = {}
    later_event = []

    def __init__(self):
        self.systems[self.name] = self
        self.disabled = False
        module = importlib.import_module(name=self.__module__)
        self.loaded_at = os.path.getmtime(module.__file__)
        self.setup()

    def setup(self):
        pass

    @property
    def name(self):
        return self.__class__.__name__

    def subscribe(self, event, handler):
        if event not in self.subscriptions:
            self.subscriptions[event] = []
        # TODO: Reloaded systems trying to handle the same events?
        self.subscriptions[event].append((self, handler))

    @classmethod
    def dispatch(cls, event, **kwargs):
        for subscriber, handler in cls.subscriptions.get(event, []):
            subscriber.reload()
            if subscriber.disabled:
                continue
            try:
                handler(**kwargs)
            except SystemExit:
                # Exit exceptions should be allowed through
                raise
            except:
                # All other exceptions should disable the system until next reload
                traceback.print_exc()
                subscriber.disabled = True
                print(f"Disabled system {subscriber} during {event} with args {kwargs}")

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
                print(f"Disabled system {system} during update")
        Entity.clean_pending_destruction()


