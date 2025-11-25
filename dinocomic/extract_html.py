from bs4 import BeautifulSoup
import os
import sys
import pathlib
import shutil
import abc


class ImageExtractor(abc.ABC):

    def run(self):
        path = pathlib.Path(self.document_location)


        assert path.is_dir(), "not a directory"
        file_name = self.output_file_name

        with open(file_name,"w") as f:
            for file in path.iterdir():
                print(file,type(file))
                
                with open(file,"r",encoding="utf-8") as f2:
                    text = f2.read()
                    image_source = self.find_image(text)
                print(image_source)
                print(image_source,sep="\n",file=f)

    @property
    @abc.abstractmethod
    def document_location(self) -> str:
        raise NotImplementedError()
    
    @property
    @abc.abstractmethod
    def output_file_name(self) -> str:
        raise NotImplementedError()


    def find_image(self,text:str):
        """
        Find image url in the provide html.
        """
        raise NotImplementedError()


class SofterWorldExtractor(ImageExtractor):

    @property
    def document_location(self):
        return "softer_world_html"
    @property
    def output_file_name(self):
        return "softer_world_url3.txt"
    def find_image(self, text):

        h = BeautifulSoup(text,features="html.parser")
        
        img = h.find("div",id="comicimg").find("img")
        if img is not None:
            return img["src"]
        return 

class DinoQwantzExtractor(ImageExtractor):
    @property
    def document_location(self):
        return "dino_qwantz"
    @property
    def output_file_name(self):
        return "dino_comic_urls1.txt"
    
    def find_image(self, text):
        h = BeautifulSoup(text,features="html.parser")
        return h.find("img",class_="comic")["src"]

def extract_img(text,pattern):

    h = BeautifulSoup(text,features="html.parser")
    
    img = h.find("div",id="comicimg").find("img")
    if img is not None:
        return img["src"]

def extract_dino(text):

    h = BeautifulSoup(text,features="html.parser")
    return h.find("img",class_="comic")["src"]



def main(): 

    extractor = DinoQwantzExtractor()
    # extractor = SofterWorldExtractor()

    extractor.run()

    return
    path = pathlib.Path("dino_qwantz")


    assert path.is_dir(), "not a directory"

    with open("dino_comics_urls1.txt","w") as f:
        for file in path.iterdir():
            print(file,type(file))
            
            with open(file,"r",encoding="utf-8") as f2:
                text = f2.read()
                image_source = extract_dino(text)
            print(image_source)
            print(image_source,sep="\n",file=f)


    pass
if __name__ == "__main__":
    main()
