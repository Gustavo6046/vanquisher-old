"""
The raymarcher

This utilizes a raymarcher to draw it at every
matching pixel. First, for each column,
the max. height on the screen is found, then
a sequence of rays with the same horizontal angle
is 'marched', coarsely checking against a "hit" function
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

import abc
import math
import time
import typing

from ..game import vector as vec

# from ..numba import maybe_numba_jit

if typing.TYPE_CHECKING:
    from .camera import Camera


class Ray:
    """
    A ray.

    Contains the X,Y position and Z height
    of the ray's current position, as well
    as angle, step size and pitch.
    """

    def __init__(self):
        """
        Constructs an initialized ray.
        """

        self.pos: vec.Vec2 = vec.vec2(0.0, 0.0)
        self.height: float = 0.0

        self.angle: float = 0.0
        self.pitch: float = 0.0

        self.step_size: float = 0.25
        self.max_hit_check: float = 0.15
        self.first_pass_coarsening: float = 1.25
        self.hit_slowing: float = 2.0

        self.max_distance: float = 150.0
        self.first_pass: bool = False
        self.hit: bool = False

        self.distance: float = 0.0
        self.height_offset: float = 0.0

    @classmethod
    def _step_offset(
        cls, angle: float, size: float, pitch: float
    ) -> typing.Tuple[typing.Tuple[float, float], float]:
        """
        Gets the step offset, both horizontal and vertical,
        with the given parameters
        """

        return (
            (
                math.cos(angle) * math.cos(pitch) * size,
                math.sin(angle) * math.cos(pitch) * size,
            ),
            math.sin(pitch) * size,
        )

    def step_offset(
        self, step_size: float
    ) -> typing.Tuple[typing.Tuple[float, float], float]:
        """
        Gets the step offset, both horizontal and vertical,
        of this ray, with the given step size.
        """

        return self._step_offset(self.angle, step_size, self.pitch)

    def next_step_offset(self) -> typing.Tuple[typing.Tuple[float, float], float]:
        """
        Gets the step offset, both horizontal and vertical,
        of this ray, with the current step size set in this
        ray.
        """

        return self.step_offset(self.step_size)

    def setup(
        self,
        pos: vec.Vec2,
        height: float,
        angle: float,
        pitch: float,
        step_size: float = 0.5,
        max_hit_check: float = 0.15,
        first_pass_coarsening: float = 1.25,
        hit_slowing: float = 2.0,
        max_distance: float = 128.0,
    ):
        """
        Configures this particular ray.
        """

        self.pos.done()
        self.pos = vec.clone(pos)

        self.height = height

        self.angle = angle
        self.pitch = pitch

        self.step_size = step_size
        self.max_hit_check = max_hit_check
        self.first_pass_coarsening = first_pass_coarsening
        self.hit_slowing = hit_slowing

        self.first_pass = True
        self.hit = False
        self.max_distance = max_distance

        self.distance = 0.0
        self.height_offset = 0.0

    def advance(self, this_step_size: float) -> typing.Tuple[vec.Vec2, float]:
        """
        Advance this ray a certain step size forward.
        """

        self.distance += this_step_size

        step_offset_xy, step_offset_z = self.step_offset(this_step_size)

        self.pos.add_tuple(step_offset_xy)

        self.height += step_offset_z
        self.height_offset += step_offset_z

        return self.pos, self.height

    def step(self) -> typing.Tuple[vec.Vec2, float]:
        """
        Steps this ray and returns the new position and height.
        """

        return self.advance(self.step_size)

    def was_hit(self) -> bool:
        """
        Recoils the ray back from the last step.

        If this ray is done marching (has hit
        with a resolution finer than max_hit_check),
        returns True, otherwise makes the step size
        finer (by dividing it by hit_slowing) and
        returns False.
        """

        # Return to previous step
        self.advance(-self.step_size)

        if self.step_size > self.max_hit_check:
            # Make step finer
            self.step_size /= self.hit_slowing

            self.first_pass = False

            return False  # not done

        self.hit = True

        return True  # done

    def was_not_hit(self):
        """
        This ray did not hit anything;
        if this is the first pass, make the
        step size coarser.
        """

        if self.first_pass:
            self.step_size *= self.first_pass_coarsening

    def __del__(self):
        """
        Discard any leftover vectors.
        """

        self.pos.done()


class Raymarcher(abc.ABC):
    """A generic raymarcher implementation.

    In order to utilize, please subclass and provide
    a `camera`, 'put' and `ray_hit` method
    implementations. Feel free to override `setup`.

    This raymarcher is used in the TerrainSubrenderer to
    render the terrain of the game.
    """

    def __init__(self):
        """Initializes this raymarcher."""
        self.ray = Ray()

    @abc.abstractmethod
    def camera(self) -> "Camera":
        """The camera this Raymarcher should get perspective information from."""
        ...

    @abc.abstractmethod
    def ray_hit(self, ray: Ray) -> bool:
        """Returns True only if this ray hits relevant geometry in its position."""
        ...

    @abc.abstractmethod
    def put(self, x: int, y: int, distance: float, ray: Ray):
        """
        Once a ray is marched, use its results for the corresponding
        pixel before proceeding, e.g. to plot a pixel colour depending
        on the distance.

        Only called if the ray hits anything.
        """

    def setup_ray(self, size: typing.Tuple[int, int], x: int, y: int, **kwargs):
        """
        Sets up this raymarcher's Ray toward the given pixel.
        """

        angle, pitch = self.camera().pixel_angle(x, y, size)

        self.ray.setup(self.camera().pos, self.camera().height, angle, pitch, **kwargs)

    def march(self) -> bool:
        """
        Marches a ray, until it really hits something.

        Returns True if it hit anything, or False
        if it went beyond the maximum distance instead.
        """

        while self.ray.distance < self.ray.max_distance:
            self.ray.step()

            if not self.ray_hit(self.ray):
                self.ray.was_not_hit()
                continue

            if self.ray.was_hit():
                # We're done!
                return True

        # We're also done! But the ray did not hit.
        return False

    def raymarch_one(
        self, size: typing.Tuple[int, int], x: int, y: int, **kwargs
    ) -> bool:
        """
        Raymarches the given pixel according to the given screen size.

        Accepts keyword parameters to be passed to Ray.setup.

        Returns True if anything was hit; False otherwise. Note that
        self.put is not called if nothing is hit.
        """

        self.setup_ray(size, x, y, **kwargs)

        hit = self.march()

        if hit:
            print(" * ", end="")
            self.put(x, y, self.ray.distance, self.ray)

        else:
            print("   ", end="")

        return hit

    def raymarch_all(self, size: typing.Tuple[int, int], **kwargs):
        """
        Raymarches all the pixels within this
        size region.

        Accepts keyword parameters to be passed to Ray.setup
        each time.
        """

        width = size[0]
        area = width * size[1]
        elapsed = 0.0

        start = time.time()

        for pos in range(area):
            elapsed += time.time() - start
            start = time.time()

            print(
                "\rRaymarching: {}/{} ({:.2f}%) - elapsed: {:.1f}s, ETA: {:.1f}s   ".format(
                    pos,
                    area,
                    100.0 * pos / area,
                    elapsed,
                    elapsed * (area - pos) / (pos + 1),
                ),
                end="",
            )

            x = pos % width
            y = math.floor(pos / width)

            self.raymarch_one(size, x, y, **kwargs)

        print("\n")
