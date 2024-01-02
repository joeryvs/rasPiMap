import urllib.request
import urllib.response
import itertools
import pathlib
from bs4 import BeautifulSoup

def web_url(n:int) -> str :
    return f"https://xkcd.com/{n}/"


def getImageList_Lower(): 
    for x in itertools.count(1):
        my_url = web_url(x)
        img = comicUrl(my_url)
        if img is None:
            return 
        yield img

def getImageList_Upper():
    for x in itertools.count(405):
        my_url = web_url(x)
        img = comicUrl(my_url)
        if img is None:
            return 
        yield img

def saveImageList(file):
    with open(file=file,mode="w") as f:
        for line in getImageList():
            print(line,file=f)

def comicUrl(url):
    with urllib.request.urlopen(url=url) as response:
        if 200 <= response.status < 300: 
            textt = response.read().decode("utf-8")
        else:
            return None
    soup = BeautifulSoup(textt,features="html.parser")
    outer = soup.find("div",id = "comic")
    imgAttr = outer.findChild("img")
    return imgAttr["src"]

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
    url2 = "https:" + "//imgs.xkcd.com/comics/convincing_pickup_line.png"
    with urllib.request.urlopen(url2) as response:
        if response is None :
            return
        if response.status != 200:
            print ("no file")
            return 
        with open("raven_3.jpg","wb") as f:
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
        # saveImageList(pathlib.Path("comics.txt"))
        ravenScrape()
    finally:
        pass

    pass

if __name__ == "__main__":
    main()
