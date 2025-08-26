import itertools
import math
import json
import array


def isPriem(num: int) -> bool:
    w = int(math.sqrt(num))
    for a in range(2, w+1):
        if num % a == 0:
            return False
    return num > 1


def isPriem2(num: int) -> bool:
    w = int(math.sqrt(num))
    ans = [b for b in range(2, w) if num % b == 0]
    return not ans


def isPriem3(num: int) -> bool:
    return not list(filter(lambda x: num % x == 0, range(2, int(math.sqrt(num))+1)))


def isPriem4(number: int) -> bool:
    return not any(filter(lambda x: number % x == 0, range(2, int(math.sqrt(number)) + 1)))


def looping() -> list[int]:
    ans = set()
    try:
        for m in itertools.count(1):
            if isPriem4(m):
                ans.add(m)
    except KeyboardInterrupt:
        pass
    return ans


class BitSet:
    def __init__(self,n):
        arrLen = math.ceil(n / 8)
        self.__array = array.array("B",[0 for _ in range(arrLen)])
        self.__len = n
        pass

    def __len__(self):
        return self.__len

    def __getitem__(self, name):
        x,y = divmod(name,8)
        answer = self.__array[x] & (1 << y)
        return bool(answer)
    
    def __setitem__(self, name, value):
        x,y = divmod(name,8)
        if value:
            self.__array[x] = self.__array[x] | (1 << y)
        else:
            self.__array[x] = self.__array[x] & ~(1 << y)
    def fillTrue(self):
        for i in range(len(self.__array)):
            self.__array[i] = (1<<8) -1
        pass

        



def wheelPrime(n:int):
    arr = [True] * n 

    arr[0] = False
    arr[1] = False
    return wheelPrimeLoop(arr,n)

def wheelPrime2(n:int):
    arr = BitSet(n)
    arr.fillTrue()
    arr[0] = False
    arr[1] = False
    return wheelPrimeLoop(arr,n)



def wheelPrimeLoop(arr,n:int):
    for i in range(n):
        if arr[i]:
            for j in range(i*i,n,i):
                arr[j] = False


    return [i for i,bool in enumerate(arr) if bool]


def toFile(object: any, filenaam="WIP.json") -> None:
    with open(filenaam, 'w') as f:
        json.dump(object, f, skipkeys=True, ensure_ascii=True,
                  allow_nan=False, indent=4)
    return


def main():
    y = wheelPrime(400)
    print(y)
    y2 = wheelPrime2(400)
    print(y2)
    return
    g = looping()
    print("interrupt happened")
    print(g)
    toFile(g)
    print("Done")
    pass


if __name__ == "__main__":
    main()
