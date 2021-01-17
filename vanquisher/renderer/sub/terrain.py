"""
The terrain subrenderer.

Uses the raymarcher module to render
the terrain.
"""

import functools
import math
import typing

from ...util import interpolate_color
from ..raymarcher import Ray, Raymarcher
from . import Subrenderer

if typing.TYPE_CHECKING:
    from ...game.world import World
    from .. import Renderer, surface
    from ..camera import Camera
    from ..surface import FramebufferSurface


class TerrainRaymarcher(Raymarcher):
    """The terrain raymarcher."""

    def __init__(
        self,
        subrenderer: "TerrainSubrenderer",
        bluishness: float = 1.4,
        scale: float = 32.0
    ):
        """Sets this raymarcher up, in this case b setting its subrenderer."""
        super().__init__()

        self.subrenderer = subrenderer
        self.bluishness = bluishness
        self.scale = scale

    @functools.lru_cache()
    @classmethod
    def _bluishness_log(cls, bluishness: float) -> float:
        """The logarithm of a distance bluishness."""
        return math.log(bluishness)

    @property
    def bluishness_log(self) -> float:
        """The logarithm of this terrain raymarcher's distance bluishness."""
        return self._bluishness_log(self.bluishness)

    @property
    def camera(self) -> "Camera":
        """Gets this Raymarcher's camera."""
        return self.subrenderer.camera

    @property
    def world(self) -> "World":
        """Gets the world whose terrain this raymarcher is rendering."""
        return self.subrenderer.world

    @property
    def draw_surface(self) -> typing.Optional["surface.FramebufferSurface"]:
        """The surface this raymarcher is rendering to."""
        return self.subrenderer.renderer.current_surface

    def ray_hit(self, ray: Ray) -> bool:
        """A callback to check when the ray is inside rendered geometry.

        Checks whether the ray has hit relevant geometry in its current
        position; in this case, terrain.
        """

        chunk = self.world.chunk_at_pos(ray.pos)
        terrain_height = chunk.terrain[ray.pos.as_tuple()]

        return ray.height < terrain_height

    def get_color(
        self, distance: float, height_offset: float
    ) -> typing.Tuple[float, float, float]:
        """Gets the current pixel's color depending on the ray's distance and depth."""

        # Get bluishness from distance
        # (air refracting light type thing?)
        bluishness = 1.0 - (
            1.0 / (1.0 + math.log(distance / self.scale + 1.0) / self.bluishness_log)
        )
        blue = (0.1, 0.4, 0.8)

        # Get brightness from vertical offset
        if height_offset < 0:
            # This ray goes down; going down makes the grass dark.
            light_green = (0.4, 0.7, 0.4)
            dark_green = (0.02, 0.15, 0.1)

            darkness = 1.0 / (1.0 + math.log(-height_offset))
            green = interpolate_color(light_green, dark_green, darkness)

        else:
            # This ray goes down; going up makes the grass closer to the sky.
            light_green = (0.4, 0.7, 0.4)
            sky_green = (0.5, 0.82, 0.6)

            skyness = 1.0 / (1.0 + math.log(height_offset))
            green = interpolate_color(light_green, sky_green, skyness)

        return interpolate_color(green, blue, bluishness)

    def put(self, x: int, y: int, distance: float, ray: Ray):
        """Puts the current pixel according to the ray's hit status."""
        if self.draw_surface is not None:
            self.draw_surface.plot_pixel(
                x, y, self.get_color(distance, ray.height_offset)
            )


class TerrainSubrenderer(Subrenderer):
    """The terrain subrenderer.

    Uses TerrainRaymarcher (and, by extension, Raymarcher)
    under the hood.
    """

    def __init__(self, renderer: "Renderer"):
        """Sets this Subrenderer up to have a raymarcher."""
        super().__init__(renderer)

        self.raymarcher = TerrainRaymarcher(self)

    def render(self, surface: "FramebufferSurface"):
        """Renders the terrain using the raymarcher."""
        self.raymarcher.raymarch_all(surface.get_size())
