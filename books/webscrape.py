import urllib.request
import urllib.response
import itertools
import pathlib
from bs4 import BeautifulSoup
import html.parser

def scrapeloop(the_paths):
    for my_url in the_paths:
        print(my_url)
        if not my_url:
            continue
        my_url = "https://boyter.org" + my_url
        pa = pathlib.Path(my_url)
        my_file = pathlib.Path("book_folder",pa.parts[-1])
        if my_file.exists():
            continue
        print(my_url,my_file)
        with urllib.request.urlopen(my_url) as response:
            if response is None :
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
    print(repr(url));
    if url.startswith("//"):
        return True 
    return False 


def book_cover_urls():
    p = "https://boyter.org/2016/04/collection-orly-book-covers/"
    with urllib.request.urlopen(p) as f:
        data = f.read()
    print(data)
    tree = BeautifulSoup(data,features="html.parser")
    images = tree.find_all("img",recursive=True)
    print(len(images))
    sources = [img["src"] for img in images]
    good_sources = ["https://boyter.org"  + source for source in sources]
    with open("book_covers2.txt","w") as fw:
        for i in good_sources:
            print(i,file=fw)


def main():
    book_cover_urls()
    return;
    try:
        print("start of scraping")
        with open("book_covers.txt","r") as f:
            g = f.readlines()
        print(len(g))
        z = (x.removesuffix("\n") for x in g)
        # z = list(z)
        # print(len(z))
        scrapeloop(z)
        print("end of scraping")
        # saveImageList(pathlib.Path("comics4.txt"))
    finally:
        pass

    pass

if __name__ == "__main__":
    main()
