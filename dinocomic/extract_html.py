from bs4 import BeautifulSoup
import os
import sys
import pathlib
import shutil



def extract_img(text,pattern):

    h = BeautifulSoup(text,features="html.parser")
    
    img = h.find("div",id="comicimg").find("img")
    if img is not None:
        return img["src"]
    



def main(): 
    path = pathlib.Path("softer_world_html")


    assert path.is_dir(), "not a directory"

    with open("softer_world_url3.txt","w") as f:
        for file in path.iterdir():
            print(file,type(file))
            
            with open(file,"r",encoding="utf-8") as f2:
                text = f2.read()
                image_source = extract_img(text,"div#comicimg > img")
            print(image_source)
            print(image_source,sep="\n",file=f)


    pass
if __name__ == "__main__":
    main()
