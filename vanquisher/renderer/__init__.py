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

if typing.TYPE_CHECKING:
    from ..game import Game
    from .camera import Camera
    from .sub import Subrenderer
    from .surface import FramebufferSurface


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
        """
        Initializes this renderer with a camera.
        """
        self.game = game
        self.camera = camera
        self.subrenderers: typing.List["Subrenderer"] = []
        self.current_surface: typing.Optional["FramebufferSurface"] = None

    def add_subrenderer(self, subrenderer: "Subrenderer"):
        """
        Adds a Subrendererer to this Renderer's subrendering
        pipeline.
        """
        self.subrenderers.append(subrenderer)

    def render(self, surface: "FramebufferSurface"):
        """
        Renders to the given surface, calling each
        Subrenderer in order.
        """

        self.current_surface = surface

        for subrenderer in self.subrenderers:
            subrenderer.render(surface)

        self.current_surface = None
