from .ecs import Component, field


class ScreenComponent(Component):
    component_name = "Screen Component"
    screen = field(mandatory=True)
    background = field(mandatory=True)

