"""Z-buffer wrapper for surface backends."""

import typing

if typing.TYPE_CHECKING:
    from .surface import FramebufferSurface


class ZBufferSurfaceWrapper:
    """Wraps a complaint FramebufferSurface instance with a Z-buffer."""

    def __init__(self, surface: "FramebufferSurface"):
        """Instantiates the Z-buffer wrapper with an underlying backend."""
        self.surface = surface
        self.z_buffer: typing.Dict[typing.Tuple[int, int], float] = {}

    def get_size(self) -> typing.Tuple[int, int]:
        """Regular surface size getter.

        This simply calls the underlying surface's get_size;
        this exists only for FramebufferSurface compliance.
        """
        return self.surface.get_size()

    def plot_pixel(self, x: int, y: int, rgb: typing.Tuple[float, float, float]):
        """Regular pixel plotting method.

        This simply calls the underlying surface's plot_pixel;
        this exists only for FramebufferSurface compliance.
        """
        self.surface.plot_pixel(x, y, rgb)

    def plot_rect(
        self,
        xy1: typing.Tuple[int, int],
        xy2: typing.Tuple[int, int],
        rgb: typing.Tuple[float, float, float],
    ):
        """Regular rectangle filling method.

        This simply calls the underlying surface's plot_rect;
        this exists only for FramebufferSurface compliance.
        """
        self.surface.plot_rect(xy1, xy2, rgb)

    def plot_pixel_z(
        self, x: int, y: int, depth: float, rgb: typing.Tuple[float, float, float]
    ):
        """A depth-aware plot_pixel wrapper.

        Plots the pixel if and only if depth is 'depth' is smaller
        than the corresponding Z-buffer value, or if there is no
        corresopnding Z-buffer value.

        If it is, also sets the corresponding Z-buffer value to the
        given depth.
        """
        if (x, y) in self.z_buffer and self.z_buffer[x, y] < depth:
            return

        self.z_buffer[x, y] = depth
        self.surface.plot_pixel(x, y, rgb)

    def update(self):
        """A surface frame update entrypoint.

        Automatically resets the Z-buffer as well.
        """
        self.surface.update()
        self.z_buffer = {}
