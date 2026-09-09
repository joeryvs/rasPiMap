import collections.abc
import json
import logging
import os
import time
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup

_logger = logging.getLogger(__name__)


class State(ABC):
    @abstractmethod
    def get_data_raw(self) -> str | dict:
        pass


class Scraper(ABC):
    def __init__(self, *, base_dir: str | None, wait_time=4.0) -> None:
        self.base_dir = base_dir
        self.wait_time = wait_time
        if self.base_dir is not None:
            assert os.path.isdir(self.base_dir), f"{self.base_dir} is not a directory"

    @abstractmethod
    def find_next_state(self, json_obj, prev_state) -> State | None:
        pass

    @abstractmethod
    def download_continuation(self, state):
        pass

    @abstractmethod
    def download_page(self) -> str:
        pass

    @abstractmethod
    def find_initial_state(self, soup) -> State | None:
        pass

    @abstractmethod
    def urls_from_initial(self, soup) -> list:
        pass

    @abstractmethod
    def urls_from_json(self, j) -> list:
        pass

    def run(self) -> collections.abc.Iterable:
        """Download page and start an iterative loop"""
        html_data = self.download_page()
        soup = BeautifulSoup(html_data, features="html.parser")
        ans1 = self.find_initial_state(soup=soup)
        print(ans1)
        if not ans1:
            _logger.error("No Initial State found")
            return
        jsons = self.run_loop(ans1)
        # Make jsons eager
        yield from self.urls_from_initial(soup)
        for j in jsons:
            yield from self.urls_from_json(j)

    def run_loop(self, initial_state) -> collections.abc.Iterable:
        index = 1
        state = initial_state
        while state is not None:
            _logger.info("Iteration: %s, currentState: %s", index, state)
            json_obj = self.download_continuation(state)
            # save the JSON for later
            if self.base_dir:
                out_path = os.path.join(self.base_dir, f"out_{index}.json")
                with open(out_path, "w") as f_out:
                    json.dump(fp=f_out, obj=json_obj, indent=2)
            yield json_obj

            state = self.find_next_state(json_obj, state)
            time.sleep(self.wait_time)
            index += 1

    def load_urls_from_files(self, /, html_location="", json_directory=""):
        if os.path.isfile(html_location):
            with open(html_location, "r") as file:
                soup = BeautifulSoup(file.read())
                yield from self.urls_from_initial(soup=soup)
        if os.path.isdir(json_directory):
            for file in os.listdir(json_directory):
                file = os.path.join(json_directory, file)
                with open(file, "r") as fp:
                    json_obj = json.load(fp=fp)
                    urls = self.urls_from_json(json_obj)
                    yield from urls


class EagerScraper(Scraper):
    def __init__(self, *, scraper: Scraper) -> None:
        self._scraper = scraper
        super().__init__(base_dir=scraper.base_dir, wait_time=scraper.wait_time)

    def download_continuation(self, state):
        return self._scraper.download_continuation(state)

    def download_page(self) -> str:
        return self._scraper.download_page()

    def urls_from_json(self, j) -> list:
        return list(self._scraper.urls_from_json(j=j))

    def urls_from_initial(self, soup) -> list:
        return list(self._scraper.urls_from_initial(soup=soup))

    def run(self):
        return list(self._scraper.run())

    def run_loop(self, initial_state):
        return list(self._scraper.run_loop(initial_state))


class Factory(ABC):
    @abstractmethod
    def get_scraper(self, *, base_dir: str | None, wait_time: float) -> Scraper:
        """Return a specific scraper"""

    def post_process_url(self, url: str) -> str:
        """Changes the url from the cropped version to an url which should retrieve the full size image"""
        return url

    def keep_url(self, url: str) -> bool:
        """Predicate to determine if the url should be kept"""
        return True
