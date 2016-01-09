pypbp_generator
===============
A python3 script to generate puzzles for [pypbp game](https://github.com/Ealdor/pypbp) from a CSV (black and white) or 
 JSON (color) file.

Command line interface
----------------------
> **python generator.py file max_number iterations speed speed_number**

* file: CSV or JSON file from which to generate the puzzle (with 1's and 0's).
* max_number: maximun number in the generated puzzle.
* iterations: number o fiterations per number.
* speed: speed used to generate the puzzle (1: slowest; 2: slow; 3: normal; 4: fast; 5: fastest).
* speed_number: number till argument speed is applied (recommended is 10 - 15).
* returns: a file *temp.csv* or *temp.json* with the generated puzzle.

More iterations means more complexity but can take more time to generate the puzzle (a good value is between 1 and 5). 
 There is no cap for the maximun number but if you use a number greater than 15 it can take a lot of time to  produce 
 the puzzle and is recommended to use a fast speed argument (depending on the puzzle size too).
 
Examples can be found in [puzzles_bw](/puzzles_bw) and in [puzzles_color](/puzzles_color) directories.
 
Dependencies
------------
* six
* ete3

Contact / Donations
-------------------
ealdorj@gmail.com