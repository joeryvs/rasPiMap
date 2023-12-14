import urllib.request
import urllib.response
import itertools
import pathlib

def web_url(n:int) -> str :
    return f"{n}"

def saveToFile(pic,n:int) -> None:
    filepath = pathlib.Path("myFiles",f"pic{n}.png")
    with open(filepath,"w") as f:
        pass
    pass

def requestData(url):

    with urllib.request.Request(url) as req:
        pass


def scrapeloop():

    for x in itertools.count(1):
        my_url = web_url(x)
        response = requestData(my_url)
        if response.code != 200:
            return 
        saveToFile(response.data)
        

def main():
    try:
        scrapeloop()
    finally:
        pass

    pass

if __name__ == "__main__":
    main()
