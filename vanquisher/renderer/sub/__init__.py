"""
A Subrenderer is responsible for rendering
a single aspect of the game; for instance,
the sky backdrop, the terrain, and the objects.
"""

import abc
import functools
import typing

if typing.TYPE_CHECKING:
    from .. import Renderer
    from ..surface import FramebufferSurface
    from ..camera import Camera
    from ...game import Game
    from ...game.world import World


class Subrenderer(abc.ABC):
    """
    A subrenderer. Think of it like a rendering subroutine,
    only drawing things that are relevant to it.
    """

    def __init__(self, renderer: "Renderer"):
        """
        Initializes it with the renderer.

        Feel free to override this function, but
        make sure to call super().__init__(renderer)
        if you do.
        """
        self.renderer = renderer

    @functools.property
    def camera(self) -> "Camera":
        """
        Gets the camera of this subrenderer.
        """
        return self.renderer.camera

    @functools.property
    def game(self) -> "Game":
        """
        Gets the game this subrenderer belongs to.
        """
        return self.renderer.game

    @functools.property
    def world(self) -> "World":
        """
        Gets the world this subrenderer is supposed
        to render or otherwise display.
        """
        return self.renderer.game.world

    @abc.abstractmethod
    def render(self, surface: "FramebufferSurface"):
        """
        Renders to a surface.
        """
        ...
