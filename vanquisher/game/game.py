"""
This module is concerned with the playsim at the highest
level that can still be narrowed down to "just" the playsim.
"""

import typing
import uuid

from . import world
from . import objects, object_type


class Game:
    """
    The main game class that holds information about
    the playsim.

    Rendering, networking etc are handled separately.

    Rendering in the client side, in the PyGame client,
    accesses information from this class. Networking
    from both client and server side will want to make
    changes to the game state as well, to sync it with
    the network.
    """

    def __init__(self):
        self.world = world.World(self)
        self.objects: typing.Dict[uuid.UUID, objects.GameObject] = {}

        self.object_types = object_type.ObjectTypeContext(self)

    def object_create(
            self,
            kind: str,
            pos: typing.Tuple[float, float],
            *args,
            **kwargs
    ) -> objects.GameObject:
        """
        Instantiates a new object of the
        specified kind, at the specified location.

        This is a basic function mostly here for test case purposes
        and some internal functions, avoid it if you're using the
        JavaScript playsim module API.
        """

        new_obj = objects.GameObject(self.world, None, kind, pos, *args, **kwargs)

        self.object_add(new_obj)

        return new_obj

    def object_add(self, obj: objects.GameObject):
        """
        Registers an object to this playsim
        and to its respective chunk.
        """

        self.objects[obj.identifier] = obj
        self.world.object_register(obj)

    def object_remove(self, obj: objects.GameObject):
        """
        Unregisters an object from this playsim
        and from the chunk it used to live in.
        """

        self.world.object_unregister(obj)
        del self.objects[obj.identifier]
