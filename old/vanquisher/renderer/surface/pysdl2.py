"""The renderer's PySDL2 backend.

Due to PySDL2's superior efficiency,
this renders the Pygame backend
deprecated.
"""

import ctypes
import math
import typing

try:
    import sdl2  # type: ignore

except ImportError:
    SUPPORTED = False

else:
    SUPPORTED = True

    c_uint32_ptr = ctypes.POINTER(ctypes.c_uint32)

    class SDLSurfacePointer(typing.Protocol):
        """A ctypes-compliant pointer to a sdl2.SDL_Surface."""

        contents: sdl2.SDL_Surface

    class SDLWindowPointer(typing.Protocol):
        """A ctypes-compliant pointer to a sdl2.SDL_Window."""

        contents: sdl2.SDL_Window

    class SDLSurface:
        """A SDL2 backend, used when rendering the game to a SDL2 window.

        __init__ takes either a sdl2.SDL_Surface, a sdl2.SDL_Window, a
        sdl2.ext.window.Window or a pointer to either a sdl2.SDL_Surface
        or sdl2.SDL_Window.
        """

        def __init__(
            self,
            surface: typing.Union[
                sdl2.SDL_Window,
                sdl2.ext.window.Window,
                sdl2.SDL_Surface,
                SDLSurfacePointer,
                SDLWindowPointer,
            ],
        ):
            """Initializes this surface"""
            self.surface_ptr: SDLSurfacePointer
            self.window: typing.Optional[sdl2.SDL_Window]
            self.surface: sdl2.SDL_Surface

            if hasattr(surface, "contents"):
                surface = surface.contents

            if isinstance(surface, sdl2.SDL_Surface):
                self.window = None
                self.surface = surface
                self.surface_ptr = ctypes.pointer(surface)

            else:
                if isinstance(surface, sdl2.ext.window.Window):
                    surface = surface.window

                self.window = surface
                self.surface_ptr = sdl2.SDL_GetWindowSurface(surface)
                self.surface = self.surface_ptr.contents

        def get_size(self) -> typing.Tuple[int, int]:
            """Returns the size of the SDL window.

            For all intents and purposes, this is the size
            that the renderer uses.
            """
            return (self.surface.w, self.surface.h)

        def _color_int32(
            self, rgb: typing.Tuple[float, float, float]
        ) -> ctypes.c_uint32:
            """Converts a colour tuple to a SDL-friendly 32-bit colour value."""
            col_r, col_g, col_b = rgb
            rgb_int = (
                min(255, max(0, math.floor(col_r * 255.0))),
                min(255, max(0, math.floor(col_g * 255.0))),
                min(255, max(0, math.floor(col_b * 255.0))),
            )

            # Convert to uint32
            # (RGBA, where A is always 255)

            pixel_bits = ctypes.c_uint32(0x000000FF)

            pixel_bits.value |= rgb_int[0] << 24
            pixel_bits.value |= rgb_int[1] << 16
            pixel_bits.value |= rgb_int[2] << 8

            return pixel_bits

        def plot_pixel(self, x: int, y: int, rgb: typing.Tuple[float, float, float]):
            """Plots a pixel to the SDL window.

            Plots an RGB pixel at the specified position with the
            specified colour, within the sdl window.
            """
            surf_index = y * self.surface.w + x

            color_int = self._color_int32(rgb)

            pixel_array_type = ctypes.POINTER(
                ctypes.c_uint32 * (self.surface.w * self.surface.h)
            )

            ptr = ctypes.cast(self.surface.pixels, pixel_array_type)

            ptr.contents[surf_index] = color_int

        def plot_rect(
            self,
            xy1: typing.Tuple[int, int],
            xy2: typing.Tuple[int, int],
            rgb: typing.Tuple[float, float, float],
        ):
            """Fills a rectangular region with a given colour.

            This implementation uses a SDL low level function
            to fill a rectangle of the specified colour between
            the specified corners.
            """
            color_int = self._color_int32(rgb)

            rect = sdl2.SDL_Rect(*xy1, xy2[0] - xy1[0], xy2[1] - xy1[1])

            sdl2.SDL_FillRect(self.surface_ptr, rect, color_int)

        def update(self):
            """SDL window updating callback.

            Updates the SDL window if and only if there is
            a window. This is not necessary for surfaces that
            are not from windows."""
            if self.window:
                sdl2.SDL_UpdateWindowSurface(ctypes.byref(self.window))

        def __del__(self):
            """Deinitializes the SDL surface."""
            # if hasattr(self, "surface"):
            #    sdl2.SDL_FreeSurface(self.surface_ptr)
