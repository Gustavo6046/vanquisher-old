"""
The portion of the renderer preoccupied with
the terrain.

This utilizes a raymarcher to draw it at every
matching pixel. First, for each column,
the max. height on the screen is found, then
a sequence of rays with the same horizontal angle
is 'marched', coarsely checking against the terrain
at each step; if a hit is found, the step size is
halved, this is repeated a few times until we're sure
we hit the terrain. Then, the corresponding color
is set, depending on whether a hit was registered
and how far.

Ray step sizes:
    * Start out smaller depending on the downward angle
      (steeper means finer);
    * Start fine, then get coarser as nothing is hit in the
      first pass. Further passes do not coarsen the
      step size; each hit moves the ray march back and
      halves the step size before continuing, until the
      step size is below a configured minimum step size.
"""

import functools
import math
import typing

import typing_extensions as typext

from ..game import vector as vec

if typing.TYPE_CHECKING:
    from . import render, framebuffer


class Ray:
    """
    A ray.

    Contains the X,Y position and Z height
    of the ray's current position, as well
    as angle, step size and slope.
    """

    def __init__(self):
        """
        Constructs an initialized ray.
        """

        self.pos: vec.Vec2 = vec.vec2(0.0, 0.0)
        self.height: float = 0.0

        self.angle: float = 0.0
        self.slope: float = 0.0

        self.step_size: float = 0.5
        self.max_fine: float = 0.15
        self.first_pass_coarsening: float = 1.2
        self.hit_slowing: float = 2.0

        self.first_pass: bool = False

        self.distance: float = 0.0

    @classmethod
    @functools.cache
    def _step_offset(
        cls, angle: float, size: float, slope: float
    ) -> typing.Tuple[vec.Vec2, float]:
        """
        Gets the step offset, both horizontal and vertical,
        with the given parameters
        """

        return (
            vec.vec2(
                math.cos(angle) * math.cos(slope) * size,
                math.sin(angle) * math.cos(slope) * size,
            ),
            math.sin(slope) * size,
        )

    def step_offset(self, step_size: float) -> typing.Tuple[vec.Vec2, float]:
        """
        Gets the step offset, both horizontal and vertical,
        of this ray.
        """

        return self._step_offset(self.angle, step_size, self.slope)

    def setup(
        self,
        pos: vec.Vec2,
        height: float,
        angle: float,
        slope: float,
        step_size: float = 0.5,
        max_fine: float = 0.15,
        first_pass_coarsening: float = 1.25,
        hit_slowing: float = 2.0,
    ):
        """
        Configures this particular ray.
        """

        if self.pos.size:
            self.pos -= self.pos

        self.pos += pos
        self.height = height

        self.angle = angle
        self.slope = slope

        self.step_size = step_size
        self.max_fine = max_fine
        self.first_pass_coarsening = first_pass_coarsening
        self.hit_slowing = hit_slowing

        self.first_pass = True
        self.distance = 0.0

    def advance(self, this_step_size: float) -> typing.Tuple[vec.Vec2, float]:
        """
        Advance this ray a certain step size forward.
        """

        self.distance += this_step_size

        step_offset_xy, step_offset_z = self.step_offset(this_step_size)

        with step_offset_xy:
            self.pos += step_offset_xy

        self.height += step_offset_z

        return self.pos, self.height

    def step(self) -> typing.Tuple[vec.Vec2, float]:
        """
        Steps this ray and returns the new position and height.
        """

        return self.advance(self.step_size)

    def hit(self):
        """
        Recoils the ray back from the last step,
        and halves the
        """

        # Return to previous step
        self.advance(-self.step_size)

        # Make step finer
        self.step_size /= self.hit_slowing

        self.first_pass = False

    def not_hit(self):
        """
        This ray did not hit anything;
        if this is the first pass, make the
        step size coarser.
        """

        self.step_size *= self.first_pass_coarsening

    def __del__(self):
        """
        Discard any leftover vectors.
        """

        self.pos.done()


class Raymarcher:
    """
    The raymarching renderer.
    """

    def __init__(self, renderer: "render.Renderer"):
        pass

    def make_ray(self, frame: "framebuffer.Framebuffer", x: int, y: int) -> Ray:
        """
        Makes a Ray toward the given pixel.
        Width and height are taken from the
        Framebuffer.

        Position, angle.
        """
