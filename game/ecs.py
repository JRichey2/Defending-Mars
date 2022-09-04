import uuid
import json
import weakref
from pyrsistent import PClass, field


class Component:
    component_name = 'Base Component'


class Event(PClass):
    kind = field(type=str, mandatory=True)


class Entity:
    entity_index = weakref.WeakValueDictionary()
    component_index = {}

    def __init__(self):
        self.entity_id = str(uuid.uuid4())
        self.components = []
        self.entity_index[self.entity_id] = self

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.entity_id}>"

    def attach(self, component:Component):
        self.components.append(component)
        if component.component_name not in self.component_index:
            self.component_index[component.component_name] = weakref.WeakSet()
        self.component_index[component.component_name].add(self)

    @classmethod
    def with_component(cls, component_name):
        return set(cls.component_index.get(component_name, set()))

    @classmethod
    def find(cls, entity_id):
        return cls.entity_index[entity_id]


class System:
    systems = {}
    subscriptions = {}

    NAME = 'Base System'

    def __init__(self):
        self.events = []
        self.systems[self.NAME] = self

    def subscribe(self, event_kind):
        if event_kind not in self.subscriptions:
            self.subscriptions[event_kind] = []
        self.subscriptions[event_kind].append(self)

    @classmethod
    def inject(cls, event):
        for subscriber in cls.subscriptions.get(event.kind, []):
            subscriber.events.append(event)

    def update(self):
        pass

    @classmethod
    def update_all(cls):
        for system_name, system in cls.systems.items():
            system.update()


