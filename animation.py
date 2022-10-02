import turtledemo
import random
from turtledemo import rosette
from turtledemo import bytedesign
from turtledemo import chaos
from turtledemo import clock
from turtledemo import colormixer
from turtledemo import forest
from turtledemo import fractalcurves
from turtledemo import lindenmayer
from turtledemo import paint
from turtledemo import minimal_hanoi
from turtledemo import nim
from turtledemo import peace
from turtledemo import penrose
from turtledemo import planet_and_moon
from turtledemo import tree
from turtledemo import round_dance
from turtledemo import sorting_animate
from turtledemo import two_canvases
from turtledemo import yinyang
from turtledemo import __main__

functionss : list[function] = [
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
    g.main()
    g.mainloop()
    pass


if __name__ == "__main__":
    main()