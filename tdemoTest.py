import cgi
import pathlib
from traceback import print_tb
import turtledemo
import random
from turtledemo import rosette, bytedesign, chaos, clock, colormixer, forest, fractalcurves, lindenmayer, minimal_hanoi, nim, paint, peace, penrose, planet_and_moon, round_dance, sorting_animate, tree, two_canvases, yinyang, __main__

functionss = [
    rosette,
    bytedesign,
    clock,
    bytedesign,
    chaos,
    colormixer,
    forest,
    fractalcurves,
    lindenmayer,
    paint,
    minimal_hanoi,
    nim,
    peace,
    penrose,
    planet_and_moon,
    tree,
    round_dance,
    sorting_animate,
    two_canvases,
    yinyang,
    __main__
]


def main():
    g = turtledemo.__dict__.values()
    # print(g)
    # print((len(g)))
    for a in g:
        print(type(a))
        print(a)
        
    return
    print(turtledemo)
    print(type(turtledemo.__dict__) )
    for a in turtledemo.__dict__.values():
        print(a)
        print(type(a))
    pass


if __name__ == "__main__":
    main()
