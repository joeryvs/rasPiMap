import unicodedata;
import string


def iterr():
    hexx = string.hexdigits[:16]
    return (a+b+c+d for a in hexx for b in hexx for c in hexx for d in hexx)


def toChar(input: str) ->str:
    b = f"0x{input}"
    temp = ""
    # exec(F"qwer = \'\\u{comb}\'")
    exec(f"temp = \'\\u{input}\'")
    return temp


def main():
    deel = iterr()
    for a in deel:
        g = toChar(a)
        print(g)


# def main2():
hexx = string.hexdigits[:16]
print(hexx)
qwer = "\u0060"
hexxx = (f"{a}{b}{c}{d}" for a in hexx for b in hexx for c in hexx for d in hexx)
hexxx = ( a + b + c + d for a in hexx for b in hexx for c in hexx for d in hexx)

with open('unicodeLarge.txt', 'w') as f:
    for comb in hexxx:
        try:
            # temp = F"{let1}{let2}{let3}{let4}"
            exec(F"qwer = \'\\u{comb}\'")
            # print(qwer)
            print(comb, unicodedata.name(qwer), qwer, file=f, sep='\t')
        except ValueError:
            print('\t\tPrint Error occurred', file=f)
            continue

# if  __name__=="__main__":
#     main2()