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


def action(points: int):
    angle = (180*(points-2))/points
    turtle.begin_fill()
    for a in range(points*2):
        turtle.forward(200)
        turtle.left(angle)
        pass
    turtle.end_fill()
    pass


if __name__ == "__main__":
    setup()
    action(7)
    turtle.mainloop()
