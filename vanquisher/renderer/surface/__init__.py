"""The interface to implement renderer backends.

This is the common interface between Vanquisher's
renderer and backends like Pygame. This enables
abstracting Vanquisher portably.

Note that this uses abc.ABC instead of
typing.Protocol - this is a fundamental interface
and is thus defined formally, rather than
informally. This also means you HAVE to inherit it
in order to implement your own.

A few common backends are already implemented
under framebuffer.pygame, etc., but
"""

import math
import typing

import typing_extensions as typext


class FramebufferSurface(typext.Protocol):
    """A FramebufferSurface interface.

    This specifies an underlying surface, that is
    used by a renderer.
    """

    def get_size(self) -> typing.Tuple[int, int]:
        """A surface size accessor.

        Get the width and height of this framebuffer,
        in pixels.
        """
        ...

    def plot_pixel(self, x: int, y: int, rgb: typing.Tuple[float, float, float]):
        """A surface pixel setter.

        Plots an RGB pixel at the specified position with the
        specified colour.
        """
        ...

    def plot_rect(
        self,
        xy1: typing.Tuple[int, int],
        xy2: typing.Tuple[int, int],
        rgb: typing.Tuple[float, float, float],
    ):
        """A surface rectangle filling utility.

        Plots a rectangle of RGB pixels at the specified position corners,
        with the specified fill colour.
        """
        ...

    def update(self):
        """A surface frame update entrypoint.

        Updates this surface with newly plotted pixels, e.g.
        by flipping it.
        """
        ...


class SurfaceDefaultPlotFillMixin:
    """A mixin for FramebufferSurface.plot_rect

    Provides a (probably slower) fallabck for
    the rect plotting utility, that calls plot_pixel
    for every pixel of the rect.

    If you can, avoid using this. Instead, it is
    recommended to use the underlying library's
    functions and/or operate at a lower level
    whenever possible. Only use this if the library
    itself does not provide any utility whatsoever
    for drawing a rectangle.
    """

    def plot_rect(
        self: FramebufferSurface,
        xy1: typing.Tuple[int, int],
        xy2: typing.Tuple[int, int],
        rgb: typing.Tuple[float, float, float],
    ):
        """The fallback implementation of a surface rectangle filling utility.

        Plots a rectangle of RGB pixels at the specified position corners,
        with the specified fill colour.

        This fallback implementation plots it one pixel at a time; it might
        be desirable to override it if the underlying surface supports
        drawing filled rectangles directly.

        If it doesn't, the library you're using is disgusting.
        """

        x_start, y_start = xy1
        x_end, y_end = xy2

        width = x_end - x_start
        height = y_end - y_start

        area = width * height

        for pos in range(area):
            x = x_start + pos % width
            y = y_start + math.floor(pos / width)

            self.plot_pixel(x, y, rgb)
