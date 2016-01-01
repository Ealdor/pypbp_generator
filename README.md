pypbp_generator
===============
A python3 script to generate puzzles for [pypbp game](https://github.com/Ealdor/pypbp) from a CSV (black and white) or 
 JSON (color) file.

Command line interface
----------------------
> **python generator.py file max_number iterations**

* file: CSV or JSON file from which to generate the puzzle.
* max_number: maximun number in the generated puzzle.
* iterations: number o fiterations per number

More iterations means more complexity but can take more time to generate the puzzle (a good value is between 1 and 5). 
 There is no cap for the maximun number but again is you use a number greater than 20 it can take a lot of time to
 produce the puzzle.
 
Dependencies
------------
* six
* ete3

Contact / Donations
-------------------
ealdorj@gmail.com