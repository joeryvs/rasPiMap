import collections
import collections.abc
import dataclasses
import datetime
import json
import logging
import os
from urllib import parse

import requests
import utils
from base import Scraper, State
from download_utils import download_from_web
from utils import print_iter_item, unique

_logger = logging.getLogger(__name__)
VERSION = "0.1"


def _find_target_script(scripts):
    # TODO, find more reliable way, preferable with real JS
    for i, s in enumerate(scripts):
        if "display_uri" in s.text:
            return s


def _get_headers(**kwargs) -> dict[str, str]:
    # TODO, reduce same options, like referer
    headers = {
        "accept": "*/*",
        "accept-language": "nl-NL,nl;q=0.9",
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://www.instagram.com",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://www.instagram.com/miley/",
        "sec-ch-prefers-color-scheme": "light",
        "sec-ch-ua": '"Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"',
        "sec-ch-ua-full-version-list": '"Chromium";v="152.0.7977.64", "Not?A_Brand";v="24.0.0.0", "Google Chrome";v="152.0.7977.64"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-model": '""',
        "sec-ch-ua-platform": '"Linux"',
        "sec-ch-ua-platform-version": '""',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
        "x-asbd-id": "359341",
        "x-csrftoken": "knYXW4LbCkbA8xh3I6bj-D",
        "x-fb-friendly-name": "PolarisLoggedOutDesktopWWWProfilePostsTabContentQuery_connection",
        "x-fb-lsd": "AdQGzW3iZZ7BFX8LN2qf8SvcUio",
        "x-ig-app-id": "936619743392459",
        "x-ig-max-touch-points": "10",
    }
    headers = dict(y for y in [tuple(x.split(": ", 1)) for x in headers] if len(y) == 2)
    return headers


@dataclasses.dataclass(frozen=True)
class InstaState(State):
    end_cursor: str
    has_next_page: bool
    id: str

    def get_data_raw(self):

        data_raw_dict = {
            "av": "0",
            "__d": "www",
            "__user": "0",
            "__a": "1",
            "__req": "o",
            "__hs": "20698.HYP%3Ainstagram_web_pkg.2.1...0",
            "dpr": "1",
            "__ccg": "EXCELLENT",
            "__rev": "1046611421",
            "__s": "cv7nzz%3Acqdfmc%3Aa5p711",
            "__hsi": "7680920097373117430",
            "__dyn": "7xeUjG1mxu1syaxG4Vp41twpUnwgU7SbzEdF8vyUco2qwJyE1kUhw2nVE4W0qa321Rw8G11wBz81s8hwGxu786a3a1YwBgao6C1uwoE2swlo8od8-U2zxe2GewGw9a361qw8Xxm16wa-0oa2-azo7u3C2u2J0bS1LyUaUbGxK3R08-269wr84-6o5p389oed6goK10xKi2K7E5y4U7a0EoKmUhw4rwXyEcFE461Hwj83KwRzk1jw",
            "__csr": "g9c5278YAW4Nal8I9hYYAlh4BsPmNsXtOiJj9WVCLXqCrlrqLtlOlA9syHrFSBl65BktjmGbRJvOiaJoyXYx4iCjyehQWAmJvY9T5_myZTUZmRUSgynFpdWAUCGoyiGQmDHBxi9ZxyiHX-8KfKdh9ESuKHxOqUjxy7E89pkrDK7pqx2dBCx64EOtau8BQi6AfAKunBByHQi2im4FXxqaCGl29oK5ouCynyoO2OHUjhEnwq64oy5E4V0KBG096oG0UE8o1jEng9U9kECEgDDwjbWK00zAE036swdK02gKcA8t010-bIE0hfw2L81BEG1KBg1YU4mzh0mglU1yE1-nwwEU4y6Ugw8R0Yy4kw5W1Ww2Wpo2jo0eJo0Zu014RCm10w2Zo42m0wo092o",
            "__hsdp": "giE5I4Iavn1t8y52kAyuVVlggucDiCzpojUwygBJ0MV16Et41GsqA2JyUiK7k1pwU83eQ0xO1TyA6oaUZio88iU6Kcw-w_xW0FQ78cUaUCm8wGwm87u0xU5e1gxG2e78K0MK5Q1lAw4Tw10q0P88ojw31o3fwTwmU0qnw9y1JwAw9y68K2qeho0L62O0gS8wqU1uVU0UK0qm0lG3m0ll3E8Q3h0hE96",
            "__hblp": "0i85W3y1AxW8x69h433wn8K2KdyVHz-m1oU8rh8iAz88o5610x-Vm6orByonwwghVUK4VQnwOz8fEfUuwsoCEa4dUO7olG2y9By8aE5y1MCBw-wgE5ecwgUqwzxObwbShwCz9U98Sim9xm0h60sa0A84W0K879od8bVE4u1dwioc80I20PUdU5K0fDw2v820wiE5Sfy8rxOm785y64ax658V5w8G09CwIw9W1Ky85e5U1uVU0UK0ME2cwlo5XwuE4S322qew-wio3cgW2d0Qg4q2hw",
            "__sjsp": "giE5I4Iarn6ggO8xgB9mqVVlggix-dBxfy292kh0UwiFNGgaUS4E06q2",
            "__comet_req": "7",
            "lsd": "AdQGzW3iZZ7BFX8LN2qf8SvcUio",
            "jazoest": "22273",
            "__spin_r": "1046611421",
            "__spin_b": "trunk",
            "__spin_t": "1788353570",
            "__crn": "comet.igweb.PolarisLoggedOutDesktopWWWProfileRoute",
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "PolarisLoggedOutDesktopWWWProfilePostsTabContentQuery_connection",
            "server_timestamps": "true",
            "variables": {
                "after": self.end_cursor,
                "first": 12,
                "id": self.id,
            },
            "doc_id": "27389614800735091",
        }
        data_raw = parse.urlencode(data_raw_dict)
        return data_raw


class InstaScraper(Scraper):
    def __init__(self, *, base_dir, wait_time, base_url, html_save_location: str | None = None) -> None:
        self.base_url = base_url
        self.html_save_location = html_save_location
        super().__init__(base_dir=base_dir, wait_time=wait_time)

    def download_continuation(self, state):

        url = "https://www.instagram.com/api/graphql"

        data_raw = state.get_raw_data()
        headers = _get_headers()
        res = requests.post(url=url, cookies=None, headers=headers, allow_redirects=True, data=data_raw)

        json_obj = res.json()
        return json_obj

    def download_page(self) -> str:
        headers = _get_headers()
        res = requests.get(url=self.base_url, timeout=30000, headers=headers, allow_redirects=True, verify=None)

        data = res.content.decode("utf-8")
        if self.html_save_location:
            with open(self.html_save_location, "w") as f:
                print(data, file=f)

        return data

    def urls_from_initial(self, soup) -> list:
        scripts = soup.find_all("script")
        target_script = _find_target_script(scripts)
        if target_script is None:
            _logger.warning("No script found")
            return []

        x = json.loads(target_script.text or "")
        p = utils.find_keys_rec(x, "display_uri", with_path=True)

        return [z for _, z in p]

    def urls_from_json(self, j) -> list:
        urls = utils.find_keys_rec(j, "display_uri", False)
        return urls

    def find_initial_state(self, soup):
        scripts = soup.find_all("script")
        target_script = _find_target_script(scripts)
        if target_script is None:
            _logger.warning("No Valid script found")
            return None
        x = json.loads(target_script.text)
        page_info = utils.find_key_rec(x, "page_info")
        print(page_info)
        if not isinstance(page_info, dict):
            _logger.warning("page info is not a dict, is type %s , with value %s", type(page_info), str(page_info))
            return None
        id_ = utils.find_key_rec(x, "xig_user_by_username")
        print(id_)
        if id_ is None:
            return None
        id_ = id_["id"]
        assert isinstance(id_, str), f"{type(id_)} should be str"
        state = InstaState(
            end_cursor=page_info.get("end_cursor", ""), has_next_page=page_info.get("has_next_page", False), id=id_
        )
        return state

    def find_next_state(self, json_obj, prev_state) -> InstaState | None:
        page_info = utils.find_key_rec(json_obj, "page_info")

        _logger.info("PAGE INFO: %s", page_info)
        if page_info is None:
            return None
        if not isinstance(page_info, dict):
            return None
        state = InstaState(
            end_cursor=page_info.get("end_cursor", ""),
            has_next_page=page_info.get("has_next_page", False),
            id=prev_state.id,
        )
        _logger.info("STATE: %s", state)
        if not state.has_next_page:
            _logger.info("Current state has no next page returning None")
            return None
        return state


def full_scrape_user(
    user: str, wait_time: float, *, save_json: bool, save_urls: bool, save_temp_urls: bool, eager: bool
):

    _logger.debug("Scraping user %s", user)
    json_directory = datetime.datetime.now(tz=datetime.timezone.utc).strftime("{}-%Y-%j").format(user)
    if os.path.isdir(json_directory):
        # Early return because the existence of the directory implies this user is already scraped
        _logger.warning("User %s has already been scraped today", user)
        return
    if save_json:
        os.makedirs(json_directory)
    else:
        json_directory = None

    base_url = f"https://www.instagram.com/{user}/"
    scraper = InstaScraper(base_url=base_url, wait_time=wait_time, base_dir=json_directory)
    all_urls = scraper.run()
    if eager:
        all_urls = list(all_urls)
    if save_temp_urls:
        all_urls = print_iter_item(f"{user}-insta-full-temp-urls.txt", all_urls)

    urls = all_urls
    # urls = (x for x in all_urls if x.startswith("https://yt3.ggpht.com"))
    if save_temp_urls:
        urls = print_iter_item(f"{user}-insta-full-filtered-urls.txt", urls)
    input_file = f"{user}-insta-full-urls.txt"
    if save_urls:
        urls = print_iter_item(input_file, urls)
    if eager:
        urls = list(urls)
    directory_prefix = f"{user}-full"
    download_from_web(urls, target_directory=directory_prefix, overwrite=True, update_extension=True)


def main():

    from argparse import ArgumentParser, BooleanOptionalAction

    parser = ArgumentParser()

    parser.add_argument("users", nargs="+")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("--wait-time", type=float, default=4.0)
    parser.add_argument("--save-html", action=BooleanOptionalAction, default=True)
    parser.add_argument("--save-json", action=BooleanOptionalAction, default=True)
    parser.add_argument("--save-urls", action=BooleanOptionalAction, default=True)
    args = parser.parse_args()

    users = args.users
    wait_time = args.wait_time
    save_html = args.save_html
    save_json = args.save_json
    save_urls = args.save_urls
    for user in users:
        full_scrape_user(
            user,
            wait_time=wait_time,
            save_json=save_json,
            save_temp_urls=save_urls,
            save_urls=save_urls,
            eager=True,
        )


if __name__ == "__main__":
    main()
