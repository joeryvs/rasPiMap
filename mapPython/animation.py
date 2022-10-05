import turtledemo
import random
from turtledemo import rosette, bytedesign, chaos, clock, colormixer, forest, fractalcurves,\
    lindenmayer, minimal_hanoi, nim, paint, peace, penrose, planet_and_moon,\
    round_dance, sorting_animate,    tree, two_canvases, yinyang, __main__

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
    g = random.choice(functionss)
    print(g)
    g.main()
    g.mainloop()
    
    pass


if __name__ == "__main__":
    main()
