"""
The camera holds some information
about a viewpoint, that is useful
for rendering, for obvious reasons.
"""


import functools
import math
import typing

from ..game import vector as vec


class Camera:
    """
    A camera. Allows moving and rotating,
    and provides access to some perspective
    and viewpoint related utilities.
    """

    def __init__(
        self,
        pos: vec.Vec2,
        height: float,
        angle: float = 0.0,
        pitch: float = 0.0,
        fov: float = 90.0,
    ):
        """
        Initializes this camera with a bunch
        of perspective related parameters.
        """
        self.pos = vec.clone(pos)
        self.height = height

        self.angle = angle
        self.pitch = pitch

        self.fov = fov

    @classmethod
    @functools.lru_cache()
    def _fov_tan(cls, fov):
        """
        The tangent of the width angle of the field of view.
        """
        return math.tan(math.radians(fov) / 2.0)

    def fov_tan(self):
        """
        The tangent of the width angle of this raymarcher's
        field of view.
        """
        return self._fov_tan(self.fov)

    def move(self, offset: vec.Vec2, height: typing.Optional[float] = None):
        """
        Moves this camera by an offset,
        and optionally height too.

        The offset must be a vec.Vec2.
        Tuples are not supported.
        """

        self.pos += offset

        if height is not None:
            self.height += height

    def rotate(self, yaw: float = 0, pitch: float = 0):
        """
        Rotates on either the yaw axis, the
        pitch axis, or both.

        The angles must be in radians.
        """

        self.angle += yaw
        self.pitch += pitch

    def screen_angle(self, x: float, y: float) -> typing.Tuple[float, float]:
        """
        Gets the angle that a ray projecting outward
        from this camera would be if the ray were
        cast at the given screen coordinates.

        The screen coordinates must be in the range between
        (-1,1). Also, y must go up, not down.

        Returns a (angle, pitch) tuple.

        ### Screen ratios

        If the size of the screen is not square, x and y
        will be scaled down until only the longest side
        of the screen rectangle results in an amplitude
        of 1 in the corresponding axis.

        In other words, a screen that is wider than it is
        tall should have X be -1 in the leftmost corners and
        1 in the rightmost ones, but Y should never reach
        either value.

        The pixel_angle method accomplishes that by dividing
        both the X and Y pixel positions by the largest value
        of either width and height, rather than dividing x by
        width and y by height.

        This is more of a guideline, though, not a hard rule;
        for instance, if you want to render to a square surface
        where your pixels are for some reason wider (or thinner)
        than they should be, resulting in unequal pixel width and
        height, you can use screen_angle instead of pixel_angle,
        and pass your own x,y values between -1 and 1.
        """

        angle = self.angle + x * self.fov_tan()
        pitch = self.pitch + y * self.fov_tan()

        return (angle, pitch)

    def pixel_angle(
        self, x: float, y: float, screen_size: typing.Tuple[int, int]
    ) -> typing.Tuple[float, float]:
        """
        Gets the angle that a ray projecting outward
        from this camera would be if the ray were
        cast at the screen cordinates corresopnding to
        the given pixel.

        The pixel coordinates are integer; they're rescaled
        and passed to screen_angle, according to the
        screen_size passed.

        Returns a (angle, pitch) tuple.
        """

        width, height = screen_size
        view_width = max(width, height)

        # 'Rightness' and 'upwardness' shall be from -1 to 1.
        # Also, y is assumed to be down, so upwardness is inverted.
        # Also, the smaller axis does not reach the full amplitude
        # of the larger one.

        rightness = ((x + 0.5) / view_width) * 2 - 1
        upwardness = -(((y + 0.5) / view_width) * 2 - 1)

        return self.screen_angle(rightness, upwardness)

    def __del__(self):
        """
        Deinitializes the pos vector.
        """
        self.pos.done()
