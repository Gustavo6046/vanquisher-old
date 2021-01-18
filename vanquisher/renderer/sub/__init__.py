"""
A Subrenderer is responsible for rendering
a single aspect of the game; for instance,
the sky backdrop, the terrain, and the objects.
"""

import typing
import typing_extensions as typext

if typing.TYPE_CHECKING:
    from ...game import Game
    from ...game.world import World
    from .. import Renderer
    from ..camera import Camera
    from ..surface import FramebufferSurface


class Subrenderer(typext.Protocol):
    """Subrenderer protocol interface.

    A subrenderer. Think of it like a rendering subroutine,
    only drawing things that are relevant to it.
    """

    renderer: "Renderer"

    def __init__(self, *args, **kwargs):
        """Subrenderers should be able to specify any argument list."""
        super().__init__()
        ...

    def render(self, surface: "FramebufferSurface"):
        """Renders to a surface."""
        ...


class SubrendererUtilMixin:
    """Subrenderer utility mixin.

    Provides some useful methods that are
    available to any compliant Subrenderer.
    """

    def camera(self: Subrenderer) -> "Camera":
        """Gets the camera of this subrenderer."""
        return self.renderer.camera

    def game(self: Subrenderer) -> "Game":
        """Gets the game this subrenderer belongs to."""
        return self.renderer.game

    def world(self: Subrenderer) -> "World":
        """Life quality world getter.

        Gets the world this subrenderer is supposed
        to render or otherwise display.
        """
        return self.renderer.game.world
