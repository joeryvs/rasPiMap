from bs4 import BeautifulSoup
from urllib import request
import urllib.request

def retrieve_image_url_and_title(url:str,outerElement = "comicimg") -> None | tuple[str,str]:

    with urllib.request.urlopen(url=url) as response:
        text = response.read().decode("utf-8")

    soup = BeautifulSoup(text,features="html.parser")
    outer = soup.find("div",id=outerElement)
    if outer is None:
        return
    inner = outer.find("img")
    if inner is not None:
        return inner["src"],inner["title"]
    else:
        return None

def retrieve_softer_world():

    with open("softer_world_url","w") as f:

        for i  in range(1,1249):
            url = "https://asofterworld.com/?id=%d" % i
            print(url)
            # continue
            src,title = retrieve_image_url_and_title(url,"comicimg")
            
            print(src,file=f)
            print(title)
            # print("#" + (repr(title) if title else "No Title"), file=f)

def main():
    retrieve_softer_world()
    pass


if __name__ == "__main__":
    main()

