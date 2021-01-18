"""The sky subrenderer.

Fills the window with a colour that
matches the bluest colour of the terrain
raymarcher, but slightly brighter.
"""

import math
import typing

from ...util import interpolate_color
from .. import Renderer
from ..raymarcher import Ray, Raymarcher
from . import SubrendererUtilMixin

if typing.TYPE_CHECKING:
    from ..surface import FramebufferSurface


class SkySubrenderer(SubrendererUtilMixin):
    """The sky subrenderer.

    Simply fills the window with a blue background
    that roughly matches (but slightly brighter than)
    the bluemost colour that the TerrainSubrenderer
    can produce.
    """

    brighter = 0.04
    sky = (0.1 + brighter, 0.4 + brighter, 0.65 + brighter)

    def __init__(self, renderer: "Renderer"):
        """Initializes Subrenderer with a Renderer."""
        self.renderer = renderer

    def render(self, surface: "FramebufferSurface"):
        """The render callback, here used simply to fill the window."""
        surface.plot_rect((0, 0), surface.get_size(), self.sky)
