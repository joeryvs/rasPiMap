import itertools
import math
import json


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
    return not list(filter(lambda x: number % x == 0, range(2, int(math.sqrt(number)) + 1)))


def looping() -> list[int]:
    ans = []
    try:
        for m in itertools.count(1):
            if isPriem4(m):
                ans.append(m)
    except KeyboardInterrupt:
        pass
    return ans


def toFile(object: any, filenaam="WIP.json") -> None:
    with open(filenaam, 'w') as f:
        json.dump(object, f, skipkeys=True, ensure_ascii=True,
                  allow_nan=False, indent=4)
    return


def main():
    g = looping()
    print("interrupt happened")
    toFile(g)
    print("Done")
    pass


if __name__ == "__main__":
    main()
