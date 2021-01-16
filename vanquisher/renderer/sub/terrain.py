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
    from .. import surface

    from ..surface import FramebufferSurface

    from ..camera import Camera
    from ...game.world import World


class TerrainRaymarcher(Raymarcher):
    """
    The terrain raymarcher.
    """

    def setup(
        self,
        subrenderer: "TerrainSubrenderer",
        bluishness: float = 1.4,
        scale: float = 32,
    ):
        """
        Sets this raymarcher up, in this case
        by setting its subrenderer.
        """
        self.subrenderer = subrenderer
        self.bluishness = bluishness
        self.scale = scale

    @functools.cache
    @classmethod
    def _bluishness_log(cls, bluishness: float) -> float:
        """
        The logarithm of a distance bluishness.
        """
        return math.log(bluishness)

    @property
    def bluishness_log(self) -> float:
        """
        The logarithm of this terrain raymarcher's distance bluishness.
        """
        return self._bluishness_log(self.bluishness)

    @property
    def camera(self) -> "Camera":
        """
        Gets this Raymarcher's camera.
        """
        return self.subrenderer.camera

    @functools.cached_property
    def world(self) -> "World":
        """
        Gets the world whose terrain this raymarcher is rendering.
        """
        return self.subrenderer.world

    @property
    def draw_surface(self) -> typing.Optional["surface.FramebufferSurface"]:
        """
        The surface this raymarcher is rendering to.
        """
        return self.subrenderer.renderer.current_surface

    def ray_hit(self, ray: Ray) -> bool:
        """
        Checks whether the ray has hit relevant
        geometry in its current position; in this
        case, terrain.
        """

        chunk = self.world.chunk_at_pos(ray.pos)
        terrain_height = chunk.terrain[ray.pos.as_tuple()]

        return ray.height < terrain_height

    def get_color(
        self, distance: float, height_offset: float
    ) -> typing.Tuple[float, float, float]:
        """
        Computes a colour for the current pixel depending on the ray's
        distance and height offset.
        """

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
        """
        Puts the current pixel according to the ray's hit status.
        """
        assert self.draw_surface is not None

        self.draw_surface.plot_pixel(x, y, self.get_color(distance, ray.height_offset))


class TerrainSubrenderer(Subrenderer):
    """
    The terrain subrenderer.

    Uses TerrainRaymarcher (and, by extension, Raymarcher)
    under the hood.
    """

    def setup(self):
        """
        Sets this Subrenderer up to have a raymarcher.
        """
        self.raymarcher = TerrainRaymarcher(self)

    def render(self, surface: "FramebufferSurface"):
        """
        Renders the terrain using the raymarcher.
        """
        self.raymarcher.raymarch_all(surface.get_size())
