"""
The rendering code.

The rendering system in Vanquisher
is abstracted by a single class, Renderer,
which sequentially contains many 'sub-renderers',
each worried with rendering a specific aspect
of Vanquisher, such as the sky, the terrain, and
the objects.
"""


import typing

from ..game.vector import vec2
from .camera import Camera

if typing.TYPE_CHECKING:
    from ..game import Game
    from .sub import Subrenderer
    from .surface import FramebufferSurface


RendererType = typing.TypeVar("RendererType", bound="Renderer")


class Renderer:
    """
    The Renderer class.

    It orchestrates multiple subrendering
    routines, such as the Skybox for the
    backdrop, the Raymarcher for terrain,
    and an undecided renderer for objects.
    This pipelining makes it efficient and
    at the same time easy to test individually.
    """

    def __init__(self, game: "Game", camera: "Camera"):
        """Initializes this renderer with a camera."""
        self.game = game
        self.camera = camera
        self.subrenderers: typing.List["Subrenderer"] = []
        self.current_surface: typing.Optional["FramebufferSurface"] = None

    @classmethod
    def create(
        cls: typing.Type[RendererType],
        game: "Game",
        camera_pos: typing.Tuple[float, float, float],
        **kwargs
    ) -> RendererType:
        """Creates a new Renderer with the given camera position.

        Keyword arguments are passed to the camera's setup method.
        That includes important ones, like angle and pitch, which
        default to zero (camera pointing horizontally toward +X).
        """
        cam_x, cam_y, cam_z = camera_pos

        with vec2(cam_x, cam_y) as cam_pos:
            camera = Camera(cam_pos, cam_z, **kwargs)

        return cls(game, camera)

    def add_subrenderer(self, subrenderer: typing.Type["Subrenderer"], *args, **kwargs):
        """Add a Subrendererer to this Renderer's subrendering pipeline.

        You need to pass a Subrenderer type, not an instance; *args and **kwargs
        can be provided to initialize any parameters a specific Subrenderer
        implementation might need.
        """
        self.subrenderers.append(subrenderer(*args, **kwargs))

    def render(self, surface: "FramebufferSurface"):
        """
        Renders to the given surface, calling each
        Subrenderer in order.
        """
        self.current_surface = surface

        for subrenderer in self.subrenderers:
            subrenderer.render(surface)

        self.current_surface = None
