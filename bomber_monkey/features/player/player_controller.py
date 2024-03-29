from bomber_monkey.features.systems.entity_factory import EntityFactory
from bomber_monkey.features.physics.rigid_body import RigidBody
from bomber_monkey.utils.vector import Vector
from python_ecs.ecs import Component, sim


class PlayerController(Component):
    def __init__(self,
                 left_key,
                 right_key,
                 up_key,
                 down_key,
                 action_key
                 ):
        super().__init__()
        self.actions = {
            left_key: self.left_action,
            right_key: self.right_action,
            up_key: self.up_action,
            down_key: self.down_acrtion,
            action_key: self.special_action,
        }

        self.accel = 1

    def left_action(self, body: RigidBody):
        body.speed += Vector.create(-self.accel, 0)

    def right_action(self, body: RigidBody):
        body.speed += Vector.create(self.accel, 0)

    def up_action(self, body: RigidBody):
        body.speed += Vector.create(0, -self.accel)

    def down_acrtion(self, body: RigidBody):
        body.speed += Vector.create(0, self.accel)

    def special_action(self, body: RigidBody):
        dropper: EntityFactory = sim.get(body.eid).get(EntityFactory)
        dropper.produce(body)
