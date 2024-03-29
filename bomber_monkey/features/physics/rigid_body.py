from bomber_monkey.utils.vector import Vector
from python_ecs.ecs import Component


class RigidBody(Component):
    def __init__(self,
                 mass: float = 1,
                 pos: Vector = None,
                 speed: Vector = None,
                 accel: Vector = None,
                 ) -> None:
        super().__init__()
        self.mass = mass
        self._pos = pos or Vector.create()
        self.speed = speed or Vector.create()
        self.accel = accel or Vector.create()

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, pos):
        self._pos = pos

    def __repr__(self):
        return 'RigidBody({})'.format(self.mass)
