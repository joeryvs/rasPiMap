import turtledemo
import random
from turtledemo import rosette, bytedesign, chaos, clock, colormixer, forest, fractalcurves, lindenmayer, minimal_hanoi, nim, paint, peace, penrose, planet_and_moon, round_dance, sorting_animate, tree, two_canvases, yinyang, __main__
# import needed to not crash

def main():
    g = turtledemo.__dict__
    allUse = [g[y] for y in g if 'main' in g[y].__dir__()]
    print(len(allUse))
    h = random.choice(allUse)
    h.main()
    h.mainloop()

    pass


if __name__ == "__main__":
    main()
