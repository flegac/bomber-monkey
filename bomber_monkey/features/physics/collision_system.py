import numpy as np

from bomber_monkey.features.board.board import Board, Tiles, Cell
from bomber_monkey.features.physics.rigid_body import RigidBody
from bomber_monkey.features.physics.shape import Shape
from python_ecs.ecs import System, Entity


class PlayerCollisionSystem(System):
    def __init__(self, board: Entity):
        super().__init__([RigidBody, Shape])
        self.board: Board = board.get(Board)

    def update(self,
               body: RigidBody,
               shape: Shape) -> None:
        def stop():
            body.speed *= 0
            body.accel *= 0

        cell = self.board.by_pixel(body.pos)

        if not cell:
            return

        def is_blocker(cell: Cell, next_cell: Cell):
            wall_blocker = next_cell.tile in (Tiles.BLOCK, Tiles.WALL)
            bomb_blocker = next_cell.bomb and (cell.grid != next_cell.grid)
            return wall_blocker or bomb_blocker

        next_pos = body.pos + body.speed + body.accel

        cell_x = cell.right() if body.speed.x + body.accel.x > 0 else cell.left()
        if cell_x:
            in_range_x = abs(next_pos.x - cell_x.center.x) < self.board.tile_size.x * .8
            if in_range_x and is_blocker(cell, cell_x):
                return stop()

        cell_y = cell.down() if body.speed.y + body.accel.y > 0 else cell.up()
        if cell_y:
            in_range_y = abs(next_pos.y - cell_y.center.y) < self.board.tile_size.y * .8
            if in_range_y and is_blocker(cell, cell_y):
                return stop()

        next_cell = self.board.by_pixel(next_pos)
        if next_cell:
            in_range = np.linalg.norm(next_pos.data - next_cell.center.data) < self.board.tile_size.y * .8
            if in_range and is_blocker(cell, next_cell):
                return stop()
