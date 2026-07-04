# GameMakerMem
A live GML injector for GameMaker Studio 2.

Uses [Underanalyzer's](https://github.com/UnderminersTeam/Underanalyzer) GML compiler, huge shoutout to the [Underminers Team](https://github.com/UnderminersTeam)!
*Underanalyzer is licensed under the Mozilla Public License Version 2.0.*

---


Tested on **Pizza Tower** (*version 2022.1*) and **DELTARUNE** (*version 2022.3*), as well as on **GameMaker version 2024.13.3.268**.
It does support more versions but they weren't necessarily tested.
Unfortunately, GMM does NOT support games made using GameMaker V1 or lower, therefore it does not work with **UNDERTALE** (yet!).

---

## NEW!
GMM now has a special environment with it's own special gml functions, including:
* `gml_wait(t)` : makes the main thread wait `t` seconds.
* `gml_load(src, self, other)` : immediatly executes the gml source `src` using `self` and `other`.
* `gml_load_safe(src, self, other)` : executes the gml source `src` using `self` and `other` on the main thread.

* `debug_get_locals(l)` : gets the levels on the execution level `l` as a struct.
* `debug_get_self(l)` : gets the `self` of the execution level `l`.
* `debug_get_other(l)` : gets the `other` of the execution level `l`.
* `debug_get_script(l)` : gets the name of the script at execution level `l`.

* `array_freeze(a)` : makes the array `a` immutable.
* `array_unfreeze(a)` : makes the array `a` mutable.
* `array_frozen(a)` : returns if the array `a` is immutable.

* `script_replace(s1, s2)` : internally swaps the two scripts, functions or methods `s1` and `s2`.

* `http_get_direct(url)` : directly returns the GET result of the request to the url `url`.

---

## Features:
  * See all instances in the current room.
  * Get/set instance variables.
  * Destroy instances.
  * Go to specific rooms using room ids.
  * Execute GML in-game!

---

## How to use:
  1) Run main.py, it should install all requirements from *requirements.txt* automatically.
  2) Write the name of the desired game (or it's process id) in the input box in the top of the app, and click "Attach".
  3) All of the game's ressources will now be loaded into memory, this might freeze the app for a couple seconds.
  4) GMM is now connected, enjoy!
