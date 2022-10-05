import turtle

turtle.title = "GradenBoog"
turtle.delay(0)
turtle.speed(10)
for b in range(0,360,10):
    t1 = turtle.clone()
    t1.left(b)
    t1.fd(300)
    t1.write(f"{b}",align="center")
    del t1


print(turtle.__all__)
print(turtle.turtles())
turtle.mainloop()