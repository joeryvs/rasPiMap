import unicodedata;
import itertools
import string


def iterr():
    temp = string.hexdigits[:16]
    deel = (a+b+c+d for a in temp for b in temp for c in temp for d in temp)
    return deel


def toChar(input: str) ->str:
    b = f"0x{input}"
    temp = "kkkkkkkk"
    exec(f"temp = 0x{input}")
    return temp


def main():
    deel = iterr()
    for a in deel:
        g = toChar(a)
        print(g)


if  __name__=="__main__":
    main()