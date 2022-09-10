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
            self.component_index[component.component_name] = set()
        self.component_index[component.component_name].add(self)

    @classmethod
    def with_component(cls, component_name):
        return list(cls.component_index.get(component_name, set()))

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
        for entity in cls.pending_destruction:
            for component_name in entity.components:
                cls.component_index[component_name].discard(entity)
            cls.entity_index.pop(entity.entity_id, None)
        cls.pending_destruction = set()


class System:
    systems = {}
    subscriptions = {}
    later_event = []

    def __init__(self):
        self.systems[self.name] = self
        self.setup()

    def setup(self):
        pass

    @property
    def name(self):
        return self.__class__.__name__

    def subscribe(self, event, handler):
        if event not in self.subscriptions:
            self.subscriptions[event] = []
        self.subscriptions[event].append((self, handler))

    @classmethod
    def dispatch(cls, event, **kwargs):
        for subscriber, handler in cls.subscriptions.get(event, []):
            handler(**kwargs)

    def update(self):
        pass

    @classmethod
    def update_all(cls):
        for system_name, system in cls.systems.items():
            system.update()
        Entity.clean_pending_destruction()
