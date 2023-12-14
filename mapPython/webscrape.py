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
    for x in range(1,100):
        my_url = f"{x}"
        my_file = pathlib.Path("myFiles",f"pic{x}.png")
        (filepath,httpresponse) = urllib.request.urlretrieve(my_url,my_file)
        if httpresponse is None:
            return 
        
        

def main():
    try:
        scrapeloop()
    finally:
        pass

    pass

if __name__ == "__main__":
    main()
