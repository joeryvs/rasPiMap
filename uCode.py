
import unicodedata
import emoji
import string 


def main():
    # print(dir(emoji))
    # emoji
    # return
    for comb in range(pow(2,16),pow(2,20)+1):

        qwer = chr(comb)
        
        name = getName(qwer)
        if name and len(name) and name.isprintable() and qwer and len(qwer) and qwer.isprintable():
            print(comb, name, qwer, sep='\t')
        


def getName(character:str) -> str:
    try:
        return emoji.demojize(character)
    except ValueError:
        pass
    try:
        return unicodedata.name(character)
    except ValueError:
        return None



if __name__ == "__main__":
    main()
