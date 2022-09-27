import string
import unicodedata

hexx = string.hexdigits[:16]
print(hexx)
qwer = ""

hexxx = (f"{a}{b}{c}{d}" for a in hexx for b in hexx for c in hexx for d in hexx)
hexxx = ( a + b + c + d for a in hexx for b in hexx for c in hexx for d in hexx)

with open('unicodeLarge2.txt', 'w') as f:
    for comb in hexxx:
        try:
            # temp = F"{let1}{let2}{let3}{let4}"
            exec(F"qwer = \'\\u{comb}\'")
            # print(qwer)
            print(comb, unicodedata.name(qwer), qwer, file=f, sep='\t')
        except ValueError:
            print('\t\tPrint Error occurred', file=f)
            continue


