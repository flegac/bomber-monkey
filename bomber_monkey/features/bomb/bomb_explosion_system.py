from bomber_monkey.features.board.board import Tiles, Cell
from bomber_monkey.features.bomb.bomb import Bomb
from bomber_monkey.features.lifetime.lifetime import Lifetime
from bomber_monkey.features.physics.rigid_body import RigidBody
from bomber_monkey.game_state import GameState
from bomber_monkey.utils.vector import Vector
from python_ecs.ecs import System, sim


class BombExplosionSystem(System):

    def __init__(self, game_state: GameState):
        super().__init__([Bomb])
        self.game_state = game_state

    def update(self, bomb: Bomb, visited: set = None) -> None:
        if not visited:
            visited = set()

        entity = sim.get(bomb.eid)
        lifetime: Lifetime = entity.get(Lifetime)
        body: RigidBody = entity.get(RigidBody)

        if not lifetime or not body:
            return
        if bomb in visited or not lifetime.is_ended():
            return

        visited.add(bomb)
        cell = self.game_state.board.by_pixel(body.pos)
        if cell.tile is Tiles.WALL:
            return

        self.game_state.create_explosion(cell.center)

        for direction in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            for i in range(1, bomb.explosion_size + 1):
                propagate = self.explode(cell, Vector.create(*direction) * i, visited)
                if not propagate:
                    break

    def explode(self, cell: Cell, direction: Vector, visited: set):
        cell: Cell = cell.move(direction)
        if cell is None or cell.tile == Tiles.WALL:
            return False

        self.game_state.create_explosion(cell.center)

        if cell.bomb:
            lifetime: Lifetime = cell.bomb.get(Lifetime)
            lifetime.expire()
            self.update(cell.bomb.get(Bomb), visited)

        return cell.tile is Tiles.EMPTY
