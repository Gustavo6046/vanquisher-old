"""
Defines a pygame surface that implements the
FramebufferSurface interface.
"""

import math
import typing

import pygame

from . import FramebufferSurface


class PygameSurface(FramebufferSurface):
    """A pygame surface, used when rendering the game to a pygame window.

    __init__ takes the same parameters as
    pygame.display.set_mode; see the pygame
    documentation on how to use those.
    """

    def __init__(self, *args, **kwargs):
        """Initializes this surface, including initializing the underlying Pygame surface."""

        self.surf = pygame.display.set_mode(*args, **kwargs)

    def get_size(self) -> typing.Tuple[int, int]:
        """Returns the size of the pygame window.

        For all intents and purposes, this is the size
        that the renderer uses.
        """

        return pygame.display.get_window_size()

    def plot_pixel(self, x: int, y: int, rgb: typing.Tuple[float, float, float]):
        """Plots a pixel to the Pygame window.

        Plots an RGB pixel at the specified position with the
        specified colour, within the pygame window.
        """
        r, g, b = rgb
        rgb_int = (
            min(255, max(0, math.floor(r * 255.0))),
            min(255, max(0, math.floor(g * 255.0))),
            min(255, max(0, math.floor(b * 255.0)))
        )

        self.surf.set_at((x, y), rgb_int)

    def plot_rect(
        self,
        xy1: typing.Tuple[int, int],
        xy2: typing.Tuple[int, int],
        rgb: typing.Tuple[float, float, float],
    ):
        """Fills a rectangular region with a given colour.

        This implementation uses pygame's utilities to fill
        a rectangle of the specified colour between the
        specified corners.
        """
        self.surf.fill(rgb, (*xy1, *xy2))

    def update(self):
        """Updates the pygame surface."""
        pygame.display.flip()
