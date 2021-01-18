"""The Pygame backend of the renderer.

Defines a pygame surface that implements the
FramebufferSurface interface.
"""

import math
import typing

try:
    import pygame  # type: ignore

except ImportError:
    SUPPORTED = False

else:
    SUPPORTED = True

    class PygameSurface:
        """A pygame surface, used when rendering the game to a pygame window.

        __init__ takes a pygame.Surface instance; if you want that to be
        a new window, use pygame.display.set_mode(...). Please reference
        the PyGame documentation for more information.
        """

        def __init__(self, surface: pygame.Surface):
            """Initializes this surface, by passing a pygame Surface to it.

            You can create a pygame Surface by using pygame.display.set_mode.
            """

            self.surf = surface

        def get_size(self) -> typing.Tuple[int, int]:
            """Returns the size of the pygame window.

            For all intents and purposes, this is the size
            that the renderer uses.
            """

            return pygame.display.get_window_size()

        def _rgb_color(
            self, rgb: typing.Tuple[float, float, float]
        ) -> typing.Tuple[int, int, int]:
            """Converts a color from floating point (0.0-1.0) to 8-bit (0-255)."""
            col_r, col_g, col_b = rgb
            return (
                min(255, max(0, math.floor(col_r * 255.0))),
                min(255, max(0, math.floor(col_g * 255.0))),
                min(255, max(0, math.floor(col_b * 255.0))),
            )

        def plot_pixel(self, x: int, y: int, rgb: typing.Tuple[float, float, float]):
            """Plots a pixel to the Pygame window.

            Plots an RGB pixel at the specified position with the
            specified colour, within the pygame window.
            """
            rgb_int = self._rgb_color(rgb)

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
            self.surf.fill(self._rgb_color(rgb), (*xy1, *xy2))

        def update(self):
            """Updates the pygame surface."""
            pygame.display.flip()
