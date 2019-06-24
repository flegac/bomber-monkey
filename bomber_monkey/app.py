from enum import IntEnum
import time
from typing import Tuple

import pygame as pg
from pygame.locals import *

import pygameMenu

from pygameMenu.locals import *

from bomber_monkey.bomber_game_config import BomberGameConfig
from bomber_monkey.features.board.board import Board
from bomber_monkey.features.board.board_display_system import BoardDisplaySystem
from bomber_monkey.features.bomb.bomb_explosion import BombExplosion
from bomber_monkey.features.bomb.bomb_explosion_system import BombExplosionSystem
from bomber_monkey.features.display.display_system import DisplaySystem
from bomber_monkey.features.display.image import Image
from bomber_monkey.features.keyboard.keyboard_system import KeyboardSystem
from bomber_monkey.features.keyboard.keymap import Keymap
from bomber_monkey.features.lifetime.lifetime import Lifetime
from bomber_monkey.features.move.move_system import MoveSystem
from bomber_monkey.features.move.position import Position
from bomber_monkey.features.move.speed import Speed
from bomber_monkey.features.physics.collision_system import PlayerWallCollisionSystem
from bomber_monkey.features.physics.friction_system import FrictionSystem
from bomber_monkey.features.physics.shape import Shape
from bomber_monkey.features.lifetime.lifetime_system import LifetimeSystem
from python_ecs.ecs import sim, Entity, Component


class EntityMover(object):
    def __init__(self, avatar: Entity, dir: Tuple[int, int]):
        self.speed = avatar.get(Speed)
        self.dir = dir
        self.is_down = False

    def move(self, event):
        self.is_down = event.type == 2
        if self.is_down:
            self.speed.x += self.dir[0] * .01
            self.speed.y += self.dir[1] * .01


class AppState(IntEnum):
    APP_START = 1  # No Game launch
    IN_GAME = 2  # Game in-progress
    IN_MENU = 3  # Display menu


class App:
    def __init__(self):
        self.conf = BomberGameConfig()
        self.state = AppState.APP_START
        self.screen = init_pygame(*self.conf.grid_pixel_size)

    def main(self):
        while True:
            if self.state != AppState.IN_GAME:
                self.display_menu()
            else:
                self.run_game()

    def display_menu(self):
        pg.key.set_repeat()
        menu = pygameMenu.Menu(
            self.screen,
            *self.conf.grid_pixel_size,
            font=pygameMenu.fonts.FONT_8BIT,
            title='Bomber Monkey',
            dopause=False
        )
        if self.state > AppState.APP_START:
            menu.add_option('Back to game', self.menu_back_to_game)
        menu.add_option('New game', self.menu_new_game)
        menu.add_option('Exit', PYGAME_MENU_EXIT)

        while self.state != AppState.IN_GAME:
            events = pg.event.get()
            for event in events:
                if event.type == QUIT:
                    exit()
                if self.state > AppState.APP_START and event.type == pg.KEYUP and event.key == pg.K_ESCAPE:
                    self.menu_back_to_game()
                    break
            menu.mainloop(events)
            pg.display.flip()

    def menu_back_to_game(self):
        self.state = AppState.IN_GAME

    def menu_new_game(self):
        self.new_game()
        self.menu_back_to_game()

    def menu_background(self):
        self.screen.fill((0, 0, 0))

    def new_game(self):
        board = self.conf.board()
        avatar = self.conf.player(1, 1)

        # create heyboard handlers
        sim.create(Keymap({
            #    https://www.pygame.org/docs/ref/key.html
            pg.K_DOWN: lambda e: EntityMover(avatar, (0, 1)).move(e),
            pg.K_UP: lambda e: EntityMover(avatar, (0, -1)).move(e),
            pg.K_LEFT: lambda e: EntityMover(avatar, (-1, 0)).move(e),
            pg.K_RIGHT: lambda e: EntityMover(avatar, (1, 0)).move(e),
            pg.K_ESCAPE: lambda e: None,
            pg.K_SPACE: bomb_creator(self.conf, avatar, board)
        }))

        # init simulation (ECS)
        sim.reset_systems([
            KeyboardSystem(),
            PlayerWallCollisionSystem(board),
            MoveSystem(),
            FrictionSystem(0.995),
            BombExplosionSystem(self.conf),
            LifetimeSystem(),
            BoardDisplaySystem(self.screen, self.conf.tile_size),
            DisplaySystem(self.screen)
        ])

    def run_game(self):
        pg.key.set_repeat(1)
        while self.state == AppState.IN_GAME:
            sim.update()
            pg.display.flip()

    def suspend_game(self):
        self.state = AppState.IN_MENU


last_creation = time.time()


def bomb_creator(conf, avatar: Entity, board_entity: Entity):
    def create_bomb(event):
        global last_creation
        now = time.time()
        if now - last_creation > .5:
            last_creation = now
            pos = avatar.get(Position)
            board: Board = board_entity.get(Board)
            aligned_pos = board.align_pixel_middle(pos.data)
            sim.create(
                Position(aligned_pos[0], aligned_pos[1]),
                Speed(),
                Shape(*conf.tile_size),
                Image('resources/bomb.png'),
                Lifetime(conf.bomb_timer_length),
                BombExplosion(3)
            )

    return create_bomb


def init_pygame(screen_width, screen_height):
    pg.init()
    #  pg.key.set_repeat(1)
    # load and set the logo
    logo = pg.image.load("resources/bomb.png")
    pg.display.set_icon(logo)
    pg.display.set_caption('my game')
    screen = pg.display.set_mode((screen_width, screen_height))
    return screen


if __name__ == "__main__":
    App().main()
