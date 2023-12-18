import string
from pprint import pprint
import unicodedata


def main():
    b = string.hexdigits[:16]
    print(b)
    qwer = None
    sett = {}
    f = open('unicode.txt', 'w')

    for let1 in range(16):
        for let2 in range(16):
            try:
                qwer = chr(16 * let1 + let2)
                print(qwer)
                print(qwer, file=f)
                sett[f"{let1}{let2}"] = qwer
            except ValueError:
                print(' ', file=f)
                continue

    f.close()
    pprint(sett)
    pass


if __name__ == "__main__":
    main()
