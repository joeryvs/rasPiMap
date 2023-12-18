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

def ravenScrape():
    url2 = "https://imgs.xkcd.com/comics/the_raven.jpg"
    with urllib.request.urlopen(url2) as response:
        if response is None :
            return
        if response.status != 200:
            print ("no file")
            return 
        with open("raven_1.jpg","wb") as f:
            f.write(response.read())
def scrapeloop():
    for x in range(1000):
        my_url = f"https://hot.leanbox.us/manga/Onepunch-Man/0001-{(str(x).zfill(3))}.png"
        print(my_url)
        with urllib.request.urlopen(my_url) as response:
            if response is None :
                return
            if response.status != 200:
                print ("no file")
                return 
            my_file = pathlib.Path("OnePunch",f"pic{x}.png")
            with open(my_file,"wb") as f:
                f.write(response.read())
    return
        
        

def main():
    try:
        scrapeloop()
    finally:
        pass

    pass

if __name__ == "__main__":
    main()
