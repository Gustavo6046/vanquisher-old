"""The terrain subrenderer.

Uses the raymarcher module to render
the terrain.
"""

import math
import typing

from ...util import interpolate_color
from ..raymarcher import Ray, Raymarcher
from . import SubrendererUtilMixin
from .sky import SkySubrenderer  # to get the fog color

if typing.TYPE_CHECKING:
    from ...game.world import World
    from .. import Renderer
    from ..camera import Camera
    from ..surface import FramebufferSurface


class TerrainRaymarcher(Raymarcher):
    """The terrain raymarcher."""

    def __init__(
        self,
        subrenderer: "TerrainSubrenderer",
        fog_distance: float = 48.0,
        scale: float = 64.0,
    ):
        """Sets this raymarcher up, in this case b setting its subrenderer."""
        super().__init__()

        self.subrenderer = subrenderer
        self.scale = scale
        self.fog_distance = fog_distance

    def camera(self) -> "Camera":
        """Gets this Raymarcher's camera."""
        return self.subrenderer.camera()

    def world(self) -> "World":
        """Gets the world whose terrain this raymarcher is rendering."""
        return self.subrenderer.world()

    def draw_surface(self) -> typing.Optional["FramebufferSurface"]:
        """The surface this raymarcher is rendering to."""
        return self.subrenderer.renderer.current_surface

    def ray_hit(self, ray: Ray) -> bool:
        """A callback to check when the ray is inside rendered geometry.

        Checks whether the ray has hit relevant geometry in its current
        position; in this case, terrain.
        """

        chunk = self.world().chunk_at_pos(ray.pos)
        terrain_height = chunk.terrain[ray.pos.as_tuple()]

        return ray.height < terrain_height

    def get_color(
        self, distance: float, height_offset: float, max_distance: float
    ) -> typing.Tuple[float, float, float]:
        """Gets the current pixel's color depending on the ray's distance and depth."""

        distance = (distance / self.scale) ** 2
        darkness_denomin = 1.0 + math.sqrt(distance + 1.0)

        # Get bluishness from distance
        # (air refracting light type thing?)
        bluishness = 1.0 - (1.0 / (1.0 + math.log(distance + 1.0)))
        blue = (0.1, 0.4, 0.65)

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

        res = interpolate_color(green, blue, bluishness)

        res = (
            res[0] / darkness_denomin,
            res[1] / darkness_denomin,
            res[2] / darkness_denomin,
        )

        distance_3d = math.sqrt(distance ** 2 + height_offset ** 2)

        if distance_3d > self.fog_distance:
            fog_alpha = (distance_3d - self.fog_distance) / (
                max_distance - self.fog_distance
            )
            res = interpolate_color(res, SkySubrenderer.sky, fog_alpha)

        return res

    def put(self, x: int, y: int, distance: float, ray: Ray):
        """Puts the current pixel according to the ray's hit status."""
        canvas = self.draw_surface()

        if canvas is not None:
            canvas.plot_pixel(
                x, y, self.get_color(distance, ray.height_offset, ray.max_distance)
            )


class TerrainSubrenderer(SubrendererUtilMixin):
    """The terrain subrenderer.

    Uses TerrainRaymarcher (and, by extension, Raymarcher)
    under the hood.
    """

    def __init__(self, renderer: "Renderer"):
        """Sets this Subrenderer up to have a raymarcher."""
        self.renderer = renderer
        self.raymarcher = TerrainRaymarcher(self)

    def render(self, surface: "FramebufferSurface"):
        """Renders the terrain using the raymarcher."""
        self.raymarcher.raymarch_all(surface.get_size())
