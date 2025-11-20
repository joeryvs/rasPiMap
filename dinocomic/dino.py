import multiprocessing.pool
from bs4 import BeautifulSoup
from urllib import request
import urllib.request
import multiprocessing
import urllib.parse 
import asyncio
import aiohttp

async def fetch(url):
    """Fetch url"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def retrieve_image_url_and_title(url:str,outerElement = "comicimg") -> None | tuple[str,str]:
    """
        Download the web-page corresponding to the url

        extract the div with the id outerElement
        
        return the src and title of the inner <img> element
    """
    # with urllib.request.urlopen(url=url) as response:
    #     text = response.read().decode("utf-8")
    text = await fetch(url=url)
    
    soup = BeautifulSoup(text,features="html.parser")
    outer = soup.find("div",id=outerElement)
    if outer is None:
        return
    inner = outer.find("img")
    if inner is not None:
        return inner["src"],inner["title"]
    else:
        return None


async def retrieve_softer_world():

    async def task(i : int) -> str:

        url = "https://asofterworld.com/?id=%d" % i
        print(url)
        # continue
        src,title = await retrieve_image_url_and_title(url,"comicimg")
        
        print(src)
        print(title)
        return src
    
    tasks = [task(i) for i in range(1,1249)]
    tasks = [await t for t in asyncio.as_completed(tasks)]

    all_src = tasks

    with open("softer_world_url3","w") as f:
        for s in all_src:
            print(s,file=f)
    return all_src

def batch_retrieve():

    with multiprocessing.Pool(processes=10) as pool:
        
        pool


def main():
    asyncio.run(retrieve_softer_world())
    pass


if __name__ == "__main__":
    main()

