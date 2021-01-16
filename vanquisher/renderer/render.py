"""
The rendering system in Vanquisher
is abstracted by a single class, Renderer,
which sequentially contains many 'sub-renderers',
each worried with rendering a specific aspect
of Vanquisher, such as the sky, the terrain, and
the objects.
"""


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

    def __init__(self):
        self.subrenderers = []
