"""
Vanquisher is a simulation game.

It is split into multiple subpackages for convenience:

 * game handles the playsim in Python, including the
   world, terrain, and game objects, and loading object
   definitions from JavaScript;

 * network is concerned with the multiplayed aspect of
   Vanquisher, the protocol and the game state synchronization,
   since Vanquisher is a persistent world and the player

 * server is the implementation of the game's server, including
   the API for basic metadata, and using the network subpackage
   for, well, networking.

 * client is the PyGame client, that uses 'network' to connect
   to a server, and 'game' to predict in-game events that don't
   need extra server info to be .
"""

__version__ = "0.1.0"
