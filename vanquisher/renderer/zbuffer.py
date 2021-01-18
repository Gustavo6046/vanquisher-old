"""Z-buffer wrapper for surface backends."""

import typing

if typing.TYPE_CHECKING:
    from .surface import FramebufferSurface


class ZBufferSurfaceWrapper:
    """Wraps a complaint FramebufferSurface instance with a Z-buffer."""

    def __init__(self, surface: "FramebufferSurface"):
        """Instantiates the Z-buffer wrapper with an underlying backend."""
        self.surface = surface
        self.z_buffer = {}

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
