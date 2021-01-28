"""Terrain rendering demo."""

import ctypes
import math
import time

import pygame
import sdl2  # type: ignore
import sdl2.ext  # type: ignore

from ..game import Game
from ..game.terrain.generator.sine import SineTerrainGenerator
from ..renderer import Renderer
from ..renderer.sub.sky import SkySubrenderer
from ..renderer.sub.terrain import TerrainSubrenderer
from ..renderer.surface.pygame import PygameSurface


def demo():
    """Runs the demo."""

    # Initialize game and terrain
    game = Game()

    game.world.set_terrain_generator(
        SineTerrainGenerator(time.time(), period=50, amplitude=12)
    )

    # Initialize renderer
    renderer = Renderer.create(
        game, (0.0, -10.0, 65.0), angle=math.radians(55), pitch=math.radians(-30)
    )

    renderer.add_subrenderer(SkySubrenderer)
    renderer.add_subrenderer(TerrainSubrenderer)

    # Initialize pygame
    window = pygame.display.set_mode((500, 240))
    backend = PygameSurface(window)

    renderer.render(backend)

    running = True

    try:
        while running:
            for evt in pygame.event.get():
                if evt.type == pygame.QUIT:
                    print("Done.")
                    running = False

    except KeyboardInterrupt:
        print("Done.")
        running = False

    window.fill((0, 0, 0))
    print("Just give me one exact second so I can say: goodbye! :)")

    time.sleep(1)


if __name__ == "__main__":
    demo()
