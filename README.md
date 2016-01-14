pypbp_generator
===============
A python3 script to generate puzzles for [pypbp game](https://github.com/Ealdor/pypbp) from a CSV (black and white) or 
 JSON (color) file.

Command line interface
----------------------
> **usage: generator.py [-h] [--cores cores] file [max_number] [iterations] [speed] [speed_number]**

*positional arguments:*
  
    file          CSV or JSON file from which to generate the puzzle
    max_number    maximun number to be present in the generated puzzle (default: 2)
    iterations    number of iterations per number (default: 1)
    speed         speed used to generate the puzzle (1:slowest;2:slow;3:normal;4:fast;5:fastest) (default: 3)
    speed_number  number till argument speed is applied (default: 2)

*optional arguments:*

    -h, --help    show this help message and exit
    --cores cores  number of cores to use (default: 1)

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
