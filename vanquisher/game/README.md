This module is responsible for the playsim of Vanquisher in
the server and the PyGame frontend, which are both written
in Python. THis includes the pivotal Game, Chunk, GameObject
and World classes.

The exception is that Game-object-specific code is written
in JavaScript and thus loaded and interfaced with using js2py.

Networking code is also common code, but is contained in a
separate package, and does not concerned with the JavaScript
side at all.
