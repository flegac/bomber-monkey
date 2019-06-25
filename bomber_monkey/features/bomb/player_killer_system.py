
from bomber_monkey.bomber_game_config import BomberGameConfig
from bomber_monkey.features.bomb.player_killer import PlayerKiller
from bomber_monkey.features.physics.rigid_body import RigidBody
from bomber_monkey.features.physics.shape import Shape
from bomber_monkey.utils.collision_detector import detect_collision
from python_ecs.ecs import System


class PlayerKillerSystem(System):

    def __init__(self, conf: BomberGameConfig):
        super().__init__([PlayerKiller, RigidBody, Shape])
        self.conf = conf

    def update(self, killer: PlayerKiller, body: RigidBody, shape: Shape) -> None:
        for player in self.conf.players:
            player_body: RigidBody = player.get(RigidBody)
            player_shape: Shape = player.get(Shape)
            if detect_collision(player_body, player_shape, body, shape):
                player.destroy()
