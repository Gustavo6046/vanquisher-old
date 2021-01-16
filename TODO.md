# To-Do List

Note: the state of this document does NOT reflect, in any way, the status or
progress of completion of the project, or any part of it, anyhow.


-----

## Engine

The actual Vanquisher Engine.

#### > Planned

* Flesh out the basic infrastructure, particularly wrt terrain generation
  and playsim structure

* Add an interface to allow the game loop to be executed from any other
  context (whether it be server or client)

	* Consider using anyio for asynchronous support

		* Remember that this might require some refactoring of
		  synchronous code, depending on how much of it we want
		  to actually make async

* Basic placeholder game

	* Flesh it out more after a basic server and client are implemented
	  (see **Game** below)

* Server implementation

	* Simple metadata API for non-game clients

	* (*just maybe*) Multiple games ('rooms') per server support

		* (*just just maybe*) Peer-to-peer distribution of 'rooms'
		  between connected servers

* Client implemetation

	* Renderer (probably a raymarcher of sorts)

* Network protocol

* Web client

* ...


#### > In Progress

* Full integration of a JavaScript object API


#### > Completed

* Basic barebones code


-----


## Game

A simple game, probably Vanquisher proper, to demonstrate some of the
capabilities¹ of Vanquisher Engine.

¹ Take this with a huge grain of salt. Preferably don't believe in it at all.


#### > Planned

* Basic gameplay concepts, make plenty use of mixins for common behaviour

	* Objects that can be damaged

	* Players

	* Inventory

		* Damage modifiers (passive, like armor, and
		  active, like weapons)

	* Enemies

		* Loot tables for the enemies

		* Maybe let enemies have their own inventories
		  too, including potentially wielding weapons
		  and wearing armor and such

* More advanced and 'interesting' concepts

	* Shops, duh!


#### > In Progress

#### > Completed

* Basic example to guide the JS API


-----


A rough roadmap, if nothing else. :)
