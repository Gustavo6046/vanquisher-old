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


class Subrenderer(abc.ABC):
    """
    A subrenderer. Think of it like a rendering subroutine,
    only drawing things that are relevant to it.
    """

    def __init__(self, renderer: "Renderer"):
        """
        Initializes it with the renderer.
        """
        self.renderer = renderer

        self.setup()

    def setup(self):
        """
        Initializes and sets this subrenderer
        up, if desired.
        """

    @property
    @functools.cached_property
    def camera(self):
        """
        Gets the camera of this subrenderer.
        """
        return self.renderer.camera

    @property
    @functools.cached_property
    def game(self):
        """
        Gets the game this subrenderer belongs to.
        """
        return self.renderer.game

    @property
    @functools.cached_property
    def world(self):
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
