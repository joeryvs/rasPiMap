
import unicodedata

with open('unicodeLarge2.txt', 'w') as f:
    for comb in range(0,65536):
        try:
            # temp = F"{let1}{let2}{let3}{let4}"
            qwer = chr(comb)
            
            # print(qwer)
            print(comb, unicodedata.name(qwer), qwer, file=f, sep='\t')
        except ValueError:
            print('\t\tPrint Error occurred', file=f)
            continue


