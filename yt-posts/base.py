import argparse
import dataclasses
import datetime
import json
import logging
import os
import time
from abc import ABC, abstractmethod
from urllib.request import Request, urlopen

import requests
from bs4 import BeautifulSoup
from utils import find_key_rec, find_keys_rec

_logger = logging.getLogger(__name__)


class State(ABC):
    @abstractmethod
    def get_data_raw(self):
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

    def run(self):
        """Download page and start an iterative loop"""
        html_data = self.download_page()
        soup = BeautifulSoup(html_data, features="html.parser")
        ans1 = self.find_initial_state(soup=soup)
        print(ans1)
        if not ans1:
            _logger.error("No Initial State found")
            return []
        jsons = self.run_loop(ans1)
        # Make jsons eager
        jsons = list(jsons)
        all_urls = []
        all_urls.extend(self.urls_from_initial(soup))
        for j in jsons:
            all_urls.extend(self.urls_from_json(j))

        return all_urls

    def run_loop(self, initial_state):
        index = 1
        state = initial_state
        jsons = []
        while state is not None:
            _logger.info("Iteration: %s, currentState: %s", index, state)
            json_obj = self.download_continuation(state)
            jsons.append(json_obj)
            # save the JSON for later
            if self.base_dir:
                out_path = os.path.join(self.base_dir, f"out_{index}.json")
                with open(out_path, "w") as f_out:
                    json.dump(fp=f_out, obj=json_obj, indent=2)

            state = self.find_next_state(json_obj, state)
            time.sleep(self.wait_time)
            index += 1
        return jsons
