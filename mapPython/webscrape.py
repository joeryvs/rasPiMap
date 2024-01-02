import urllib.request
import urllib.response
import itertools
import pathlib
from bs4 import BeautifulSoup

def web_url(n:int) -> str :
    return f"https://xkcd.com/{n}/"


def getImageList_1(): 
    return getImageList(range(1,404))

def getImageList_2():
    return getImageList(range(405,1350))

def getImageList_3():
    return getImageList(range(1351,1608))

def getImageList_4():
    return getImageList(itertools.count(1609))

def getImageList(my_num_iter):
    return filter(lambda a : a is not None ,(comicUrl(web_url(x)) for x in my_num_iter))
    

def saveImageList(file):
    with open(file=file,mode="w") as f:
        for line in getImageList_4():
            print(line,file=f)

def comicUrl(url):
    with urllib.request.urlopen(url=url) as response:
        if 200 <= response.status < 300: 
            textt = response.read().decode("utf-8")
        else:
            return None
    soup = BeautifulSoup(textt,features="html.parser")
    outer = soup.find("div",id = "comic")
    if outer is None :
        return
    imgAttr = outer.findChild("img")
    if imgAttr is not None:
        return imgAttr["src"]
    else:
        return None



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


def scrapeloop(the_paths):
    for my_url in the_paths:
        my_url = pathlib.Path("https:" , my_url)
        print(my_url)
        with urllib.request.urlopen(my_url) as response:
            if response is None :
                return
            if 200 <= response.status < 300:
                pa = pathlib.Path(g)
                my_file = pathlib.Path("comics",pa.parts[-1])
                with open(my_file,"wb") as f:
                    f.write(response.read())
            else:
                print("no image")
                return 
    return
        
        

def main():
    try:
        saveImageList(pathlib.Path("comics4.txt"))
    finally:
        pass

    pass

if __name__ == "__main__":
    main()
