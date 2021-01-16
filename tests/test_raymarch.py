"""
A small suite of tests meant to test
the raymarcher.

Instead of trying to check against rendering
output (which would be basicaly impossible),
we check that rays behave like they should,
when stepping, when hit, and when not hit.
"""

import math
import typing

from vanquisher.game.vector import DEFAULT_POOL, Vec2, vec2
from vanquisher.renderer.camera import Camera
from vanquisher.renderer.raymarcher import Ray, Raymarcher

T = typing.TypeVar("T")


class GuineaRaymarcher(Raymarcher):
    """
    A Raymarcher implementation used for testing.

    Allows setting when it is hit.
    """

    def __init__(self, camera: "Camera"):
        """
        Initializes the test raymarcher.
        """
        super().__init__()

        self._camera = camera

        self.next_hit_callback = None

    @property
    def camera(self) -> "Camera":
        """
        Tells the raymarcher that _camera is
        our camera.
        """
        return self._camera

    def __call__(self: T, next_hit_callback: typing.Callable[["Ray"], bool]) -> T:
        """
        Allows using this object as a decorator to
        define the callback that decides the outcome
        of the next ray hit check for testing purposes.
        """
        self.next_hit_callback = next_hit_callback

        return self

    def ray_hit(self, ray: "Ray") -> bool:
        """
        Tells the raymarcher whether the
        current state is a hit.
        """

        if self.next_hit_callback is None:
            return False

        return self.next_hit_callback(ray)

    def put(self, x: int, y: int, distance: float, ray: Ray):
        """
        No-op, we're not interested.
        """
        ...


def test_ray():
    """
    Tests the behaviour of raymarcher rays
    to ensure they function properly.
    """

    init_free = DEFAULT_POOL.free

    guinea_ray = Ray()

    init_pos = vec2(0.0, -10.0)

    guinea_ray.setup(init_pos, 6.0, math.radians(45), math.radians(-15), step_size=0.5)

    # Verify that setting the ray up works

    assert guinea_ray.pos.x == 0.0
    assert guinea_ray.pos.y == -10.0
    assert guinea_ray.pos.size == 10.0  # pos. vector length

    assert guinea_ray.height == 6.0
    assert guinea_ray.angle == math.radians(45)
    assert guinea_ray.pitch == math.radians(-15)

    # Make sure offsets match

    step_size_1: float = guinea_ray.step_size
    offset_xy, offset_z = guinea_ray.next_step_offset
    coarsening: float = guinea_ray.first_pass_coarsening

    total_size_sq: float = offset_xy.size ** 2 + offset_z ** 2
    assert total_size_sq == guinea_ray.step_size ** 2

    assert offset_xy.size == guinea_ray.step_size * math.cos(guinea_ray.pitch)
    assert offset_z == guinea_ray.step_size * math.sin(guinea_ray.pitch)

    # Verify that stepping works, including first pass coarsening and offsets

    guinea_ray.step()
    guinea_ray.was_not_hit()

    assert not guinea_ray.hit

    with init_pos + offset_xy as new_pos_pred:
        assert guinea_ray.pos == new_pos_pred

    assert guinea_ray.height - offset_z == 6.0

    assert guinea_ray.step_size == step_size_1 * coarsening

    step_size_1_xy = step_size_1 * math.cos(guinea_ray.pitch)

    assert offset_xy.size == step_size_1_xy
    assert offset_xy.size * coarsening == guinea_ray.step_size * math.cos(
        guinea_ray.pitch
    )

    new_step_size = guinea_ray.step_size
    tot_step_size = new_step_size + step_size_1

    tot_step_size_xy = tot_step_size * math.cos(guinea_ray.pitch)

    halved_step_size = new_step_size / guinea_ray.hit_slowing

    # Pretend we hit something, and ensure
    # the behaviour is the expected.

    guinea_ray.step()
    assert not guinea_ray.hit

    with guinea_ray.pos - init_pos as diff_pos:
        assert diff_pos.size == tot_step_size_xy

    guinea_ray.was_hit()
    assert guinea_ray.hit is (guinea_ray.step_size <= guinea_ray.max_hit_check)

    assert guinea_ray.step_size == halved_step_size

    # We should be back to the position we were in after the first step.

    with guinea_ray.pos - offset_xy as old_pos:
        assert old_pos == init_pos

    assert guinea_ray.height - offset_z == 6.0

    offset_xy.done()
    del offset_xy

    init_pos.done()
    del init_pos

    guinea_ray.__del__()

    assert DEFAULT_POOL.free == init_free


def test_raymarcher():
    """
    Ensure that the generic Raymarcher implementation
    generally works as it should, by testing a general
    barebones implementation of it.
    """

    init_free = DEFAULT_POOL.free

    with vec2(0.0, 0.0) as pos:
        camera = Camera(pos, 1.0)

    size = (3, 3)
    pixel_pos = (1, 1)

    @GuineaRaymarcher(camera)
    def guinea_marcher(ray: Ray) -> bool:
        # For this test, the hit condition is having
        # a position with a X coordinate beyond five
        # in either direction.
        return abs(ray.pos.x) > 5

    ray = guinea_marcher.ray

    step_xy, step_z = ray.next_step_offset

    with step_xy:
        assert step_z == 0.0  # no camera pitch

        assert step_xy.y == 0.0  # no camera angle
        assert step_xy.x == ray.step_size  # just forward

    p_angle, p_pitch = camera.pixel_angle(1, 1, (3, 3))

    assert p_angle == camera.angle and p_pitch == camera.pitch

    # Raymarch once
    guinea_marcher.raymarch_one(size, *pixel_pos)

    # Verify results

    assert abs(ray.pos.x + ray.step_size * math.cos(ray.pitch)) > 5.0
    assert abs(ray.pos.y) == 0.0  # camera angle was zero
    assert ray.height == camera.height  # camera pitch was zero

    del guinea_marcher
    del ray
    del camera

    assert DEFAULT_POOL.free == init_free
