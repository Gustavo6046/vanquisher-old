"""Terrain rendering demo."""

import math
import time
import pygame

from vanquisher.game import Game
from vanquisher.game.terrain.generator.sine import SineTerrainGenerator
from vanquisher.renderer import Renderer
from vanquisher.renderer.sub.terrain import TerrainSubrenderer
from vanquisher.renderer.surface.pygame import PygameSurface


def demo():
    """Runs the demo."""

    # Initialize game and terrain
    game = Game()

    game.world.set_terrain_generator(SineTerrainGenerator(time.time()))

    # Initialize renderer
    renderer = Renderer.create(
        game, (0.0, -10.0, 50.0), angle=math.radians(30), pitch=math.radians(-15)
    )

    renderer.add_subrenderer(TerrainSubrenderer)

    # Initialize pygame
    window = PygameSurface((120, 120))

    renderer.render(window)

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()


if __name__ == "__main__":
    demo()
