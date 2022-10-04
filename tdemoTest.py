import pprint
import turtledemo
import random
import json
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
    pprint.pprint(turtledemo)
    g = turtledemo.__dict__
    empty = {}
    allUsefullModules = []
    for a in g:
        b  = g[a]
        empty[str(b)] = b.__dir__()
        if 'main' in b.__dir__():
            allUsefullModules.append(b)
    print(empty)
    allUse = [g[y] for y in g if 'main' in g[y].__dir__()]
    allString = [str(b) for b in allUse]
    file = "TurtleDemo instructions.json"
    with open(file, "w") as f:
        json.dump(empty, f, indent=4)
        pass
    with open("turtledemoModules.json", 'w') as f:
        json.dump(allString,f,indent=4) 
    # print(allUsefullModules)
    pass


if __name__ == "__main__":
    main()
