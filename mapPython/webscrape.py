import urllib.request
import urllib.response
import itertools
import pathlib
from bs4 import BeautifulSoup
import re

def web_url(n:int) -> str :
    return f"https://xkcd.com/{n}/"


def getImageList_1(): 
    return getImageList(range(1,404))

def getImageList_2():
    return getImageList(itertools.count(405))
    # return getImageList(range(405,1350))


def getImageList_3():
    return getImageList(range(1351,1608))

def getImageList_4():
    return getImageList(itertools.count(1609))

def getImageList(my_num_iter):
    return filter(lambda a : a is not None ,(comicUrl(web_url(x)) for x in my_num_iter))
    

def saveImageList(file):
    with open(file=file,mode="w") as f:
        for line in getImageList_2():
            print(line,file=f)

def comicUrl(url):
    with urllib.request.urlopen(url=url) as response:
        if 200 <= response.status < 300: 
            textt = response.read().decode("utf-8")
        else:
            return None
    soup = BeautifulSoup(textt,features="html.parser")
    outer = soup.find("div",id = "comic")
    if outer is None:
        return
    imgAttr = outer.find("img")
    if imgAttr is not None:
        return imgAttr["src"]
    else:
        return None



def ravenScrape():
    url2 = "https://imgs.xkcd.com/comics/the_raven.jpg"
    url2 = "https:" + "//imgs.xkcd.com/comics/convincing_pickup_line.png"
    with urllib.request.urlopen(url2) as response:
        if response is None:
            return
        if response.status != 200:
            print ("no file")
            return 
        with open("raven_3.jpg","wb") as f:
            f.write(response.read())


def scrapeloop(the_paths):
    for my_url in the_paths:
        if not my_url:
            continue
        my_url = "https:" + my_url
        pa = pathlib.Path(my_url)
        my_file = pathlib.Path("xkcd 18-08-2025",pa.parts[-1])
        if my_file.exists():
            continue
        print(my_url,my_file)
        with urllib.request.urlopen(my_url) as response:
            if response is None:
                return
            if 200 <= response.status < 300:
                data = response.read()
                with open(my_file,"wb") as f:
                    f.write(data)
            else:
                print("no image")
                return 
    return

def scapable_url(url:str)-> bool:
    if url.startswith("//"):
        return True 
    print(url,"not scrapable")
    return False 
        

def main():
    if 0:
        with open("comics_all2.txt",mode="rt",encoding="utf-8") as f:
            g = f.readlines()
        z = (x.removesuffix("\n") for x in g if scapable_url(x))
        scrapeloop(z)
    else:
        saveImageList(pathlib.Path("comics2_23-08-2025.txt"))
    

    pass

if __name__ == "__main__":
    main()
