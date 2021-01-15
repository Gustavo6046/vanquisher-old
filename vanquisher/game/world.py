"""
This module concerns with the behaviour of the world,
its basic structure, and how it contains and integrates
the objects that live and the terrain that lay in it.
"""

import math
import typing
import uuid

from . import game, objects, terrain, vector


class Chunk:
    """
    A chunk; a piece of the world that was generated ans
    is loaded in memory.
    """

    def __init__(self, world: "World", chunk_pos: typing.Tuple[int, int]):
        self.world = world
        self.chunk_pos = chunk_pos
        self.width = self.world.chunk_width
        self.terrain = terrain.TerrainChunk(self.width)

        self.objects_in_chunk: typing.Set[uuid.UUID] = set()

    @property
    def game(self):
        """
        Fetches the game whose world this chunk belongs to.
        """
        return self.world.game

    def objects_inside(self) -> typing.Generator["objects.GameObject", None, None]:
        """
        Iterates on all the objects in this chunk.
        """

        for obj_id in self.objects_in_chunk:
            yield self.game.objects[obj_id]

    def object_register(self, obj: "objects.GameObject"):
        """
        Regsiters an object to this chunk.
        """

        self.objects_in_chunk.add(obj.identifier)

    def object_unregister(self, obj: "objects.GameObject"):
        """
        Unregsiters an object from this chunk.
        """

        self.objects_in_chunk.remove(obj.identifier)


class World:
    """
    The world in which objects interact to the terrain
    and each other.
    """

    def __init__(
        self,
        my_game: "game.Game",
        terrain_generator: typing.Optional[terrain.TerrainGenerator] = None,
        chunk_width: int = 32,
        base_height: float = 32.0,
        gravity: float = -4.0,
    ):
        self.game = my_game
        self.chunk_width = chunk_width
        self.base_height = base_height
        self.terrain_generator = terrain_generator

        self.chunks: typing.Dict[typing.Tuple[int, int], Chunk] = {}

        self.gravity = gravity

    def get_chunk(self, chunk_pos: typing.Tuple[int, int]) -> Chunk:
        """
        Gets a chunk at a chunk-space position.
        """

        if chunk_pos in self.chunks:
            return self.chunks[chunk_pos]

        return self.make_chunk(*chunk_pos)

    def chunk_at_pos(
        self, pos: typing.Union[vector.Vec2, typing.Tuple[float, float]]
    ) -> Chunk:
        """
        Gets a chunk at a world-space position.
        """

        if isinstance(pos, vector.Vec2):
            pos_x, pos_y = pos.as_tuple()

        else:
            pos_x, pos_y = pos

        return self.get_chunk(
            (math.floor(pos_x / self.chunk_width), math.floor(pos_y / self.chunk_width))
        )

    def object_register(self, obj: "objects.GameObject"):
        """
        Registers a game object to the chunk it is in.

        Use `Game.oobject_register` instead. That affects the
        whole playsim.
        """

        chunk = self.chunk_at_pos(obj.pos.as_tuple())
        chunk.object_register(obj)

    def object_unregister(self, obj: "objects.GameObject"):
        """
        Unregisters a game object from the chunk it was in.

        Use `Game.oobject_unregister` instead. That affects the
        whole playsim.
        """

        chunk = self.chunk_at_pos(obj.pos.as_tuple())
        chunk.object_unregister(obj)

    def make_chunk(self, chunk_x: int, chunk_y: int) -> Chunk:
        """
        Initializes and generates a chunk at a specified
        chunk-space position.
        """

        new_chunk = Chunk(self, (chunk_x, chunk_y))
        off_x = chunk_x * self.chunk_width
        off_y = chunk_y * self.chunk_width

        if self.terrain_generator:
            new_chunk.terrain.generate(self.terrain_generator, (off_x, off_y))

        self.chunks[chunk_x, chunk_y] = new_chunk

        return new_chunk

    def update_objects(self, time_delta: float):
        """
        Updates all objects in this world.
        """

        for obj in self.game.objects.values():
            obj.tick(time_delta)
