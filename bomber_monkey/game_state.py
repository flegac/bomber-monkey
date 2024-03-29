import time
from typing import List

from bomber_monkey.features.banana.banana import Banana
from bomber_monkey.features.player.player_controller import PlayerController
from bomber_monkey.game_config import GameConfig
from bomber_monkey.features.board.board import Board, random_blocks, Tiles, fill_border, clear_corners, wall_grid
from bomber_monkey.features.bomb.bomb import Bomb
from bomber_monkey.features.systems.entity_factory import EntityFactory
from bomber_monkey.features.player.player_killer import PlayerKiller
from bomber_monkey.features.tile.tile_killer import TileKiller
from bomber_monkey.features.display.image import Image, Sprite
from bomber_monkey.features.lifetime.lifetime import Lifetime
from bomber_monkey.features.physics.rigid_body import RigidBody
from bomber_monkey.features.physics.shape import Shape
from bomber_monkey.features.player.player import Player
from bomber_monkey.utils.vector import Vector
from python_ecs.ecs import sim, Entity


class GameState(object):
    def __init__(self, conf: GameConfig, board: Board = None):
        self.conf = conf
        self._board: Board = board
        self._players: List[Entity] = []

    def _on_destroy_player(self, entity: Entity):
        player: Player = entity.get(Player)
        if player:
            self.players.remove(entity)

    @property
    def players(self) -> list:
        return self._players

    def create_player(self, grid_pos: Vector, controller: PlayerController):
        pos = grid_pos * self.conf.tile_size + self.conf.tile_size // 2

        player = sim.create(
            RigidBody(
                pos=pos
            ),
            Shape(self.conf.tile_size),
            Sprite(
                'resources/monkey_sprite.png',
                sprite_size=Vector.create(40, 36),
                anim_size=10
            ),
            Player(len(self.players) + 1, self.conf.bomb_power),
            EntityFactory(self.conf.bomb_drop_rate, self.create_bomb),
            controller
        )
        self.players.append(player)
        return player

    def create_explosion(self, pos: Vector):
        return sim.create(
            RigidBody(pos=pos),
            Shape(self.conf.tile_size // 2),
            Image('resources/fire.png'),
            Lifetime(self.conf.explosion_duration),
            PlayerKiller(),
            TileKiller(Tiles.BLOCK)
        )

    def create_board(self):
        board = Board(tile_size=self.conf.tile_size, grid_size=self.conf.grid_size)
        sim.on_create.append(board.on_create)
        sim.on_destroy.append(board.on_destroy)
        sim.on_destroy.append(self._on_destroy_player)

        random_blocks(board, Tiles.BLOCK, 1.)
        # random_blocks(board, Tiles.WALL, .5)
        clear_corners(board)
        wall_grid(board)

        fill_border(board, Tiles.WALL)
        self._board = board
        self._players = []

        return sim.create(board)

    @property
    def board(self) -> Board:
        return self._board

    def create_banana(self, body: RigidBody):
        return sim.create(
            RigidBody(
                pos=self.board.by_pixel(body.pos).center
            ),
            Shape(self.conf.tile_size),
            Sprite(
                'resources/banana_sprite32.png',
                sprite_size=Vector.create(32, 32),
                anim_size=11,
                anim_time=.5
            ),
            Banana()
        )

    def create_bomb(self, body: RigidBody):
        entity = sim.get(body.eid)
        player: Player = entity.get(Player)

        return sim.create(
            RigidBody(
                pos=self.board.by_pixel(body.pos).center
            ),
            Shape(self.conf.tile_size * 2),
            Sprite(
                'resources/bomb_sprite.png',
                sprite_size=Vector.create(32, 32),
                anim_size=13
            ),
            Lifetime(self.conf.bomb_duration),
            Bomb(player.power)
        )


last_creation = time.time()
