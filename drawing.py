import turtle
import random


def r_color():
    return (random.random(), random.random(), random.random())


def setup():
    turtle.fillcolor(r_color())
    turtle.pencolor(r_color())
    turtle.penup()
    turtle.setx(-100)
    turtle.pendown()
    pass


def action():
    turtle.begin_fill()
    for a in range(36):
        turtle.forward(200)
        turtle.left(170)
        pass
    turtle.end_fill()
    pass


if __name__ == "__main__":
    setup()
    action()
    turtle.mainloop()
