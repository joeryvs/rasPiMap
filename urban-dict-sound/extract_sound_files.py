from bs4 import BeautifulSoup
import pathlib
import abc
import re


class SoundExtractor(abc.ABC):

    def run(self):
        path = pathlib.Path(self.document_location)

        assert path.is_dir(), "not a directory"
        file_name = self.output_file_name

        with open(file_name,"w") as f:
            for file in path.iterdir():
                print(file,type(file))
                
                with open(file,"r",encoding="utf-8") as f2:
                    text = f2.read()
                    link_sources = self.find_links(text)
                for source in link_sources:
                    print(source)
                    print(source,end="\n",file=f)

    @property
    @abc.abstractmethod
    def document_location(self) -> str:
        raise NotImplementedError()
    
    @property
    @abc.abstractmethod
    def output_file_name(self) -> str:
        raise NotImplementedError()


    def find_links(self,text:str):
        """
        Find link url in the provided html.
        """
        raise NotImplementedError()


class UrbanDictionaryExtractor(SoundExtractor):
    @property
    def document_location(self):
        return pathlib.Path(__file__).parent / "html"
    
    @property
    def output_file_name(self):
        return pathlib.Path(__file__).parent / "urban_dictionary_sounds.txt"
    
    def find_links(self, text):
        
        h = BeautifulSoup(text,features="html.parser")
        
        outer_containers = h.find_all("span")
        # print("oc",outer_containers)
        for outer_container in outer_containers:
            if outer_container.has_attr("@click"):
                click_command = outer_container["@click"]
                # print("cc", click_command,type(click_command))
                extract_regex = re.compile(r"\$store.tts.play\('(\d+)', '(.*)'\)")
                m = extract_regex.search(click_command)
                if m:
                    print("match: ",m.group(2))
                    yield m.group(2)


def main(): 
    extractor = UrbanDictionaryExtractor()
    extractor.run()

if __name__ == "__main__":
    main()
