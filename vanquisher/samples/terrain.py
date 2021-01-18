"""Terrain rendering demo."""

import ctypes
import math
import time

import sdl2  # type: ignore
import sdl2.ext  # type: ignore

from ..game import Game
from ..game.terrain.generator.sine import SineTerrainGenerator
from ..renderer import Renderer
from ..renderer.sub.sky import SkySubrenderer
from ..renderer.sub.terrain import TerrainSubrenderer
from ..renderer.surface.pysdl2 import SDLSurface


def demo():
    """Runs the demo."""

    # Initialize game and terrain
    game = Game()

    game.world.set_terrain_generator(SineTerrainGenerator(time.time()))

    # Initialize renderer
    renderer = Renderer.create(
        game, (0.0, -10.0, 50.0), angle=math.radians(30), pitch=math.radians(-15)
    )

    renderer.add_subrenderer(SkySubrenderer)
    renderer.add_subrenderer(TerrainSubrenderer)

    # Initialize pygame
    window = sdl2.ext.Window("Terrain Rendering Test", (130, 130))
    backend = SDLSurface(window)

    renderer.render(backend)
    window.show()

    running = True

    while running:
        event = sdl2.SDL_Event()

        while sdl2.SDL_PollEvent(ctypes.byref(event)):
            if event.type == sdl2.SDL_QUIT:
                running = False

    window.close()


if __name__ == "__main__":
    demo()
