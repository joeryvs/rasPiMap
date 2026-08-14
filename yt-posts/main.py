import argparse
import datetime
import json
import logging
import os
import time
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from utils import find_key_rec, find_keys_rec

_logger = logging.getLogger(__name__)


class YtPostScraper:
    def __init__(self, base_dir: str, graft_url: str, /, wait_time: float = 5.0) -> None:
        self._base_dir: str = base_dir
        self.graft_url: str = graft_url
        self.wait_time: float = wait_time

        assert os.path.exists(self._base_dir) and os.path.isdir(self._base_dir), (
            "Scraping store directory does not exist"
        )

    def get_data_raw(self, continuation: str, tracking_param: str):
        return {
            "context": {
                "client": {
                    "hl": "nl",
                    "gl": "NL",
                    "remoteHost": "188.90.199.153",
                    "deviceMake": "",
                    "deviceModel": "",
                    "visitorData": "CgtvTHd2azBVVDVQMCj_7PbTBjIoCgJOTBIiEh4SHAsMDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicgI2LfAgrcAjIwLllUPVQ3OWE3VVJWR01BMTlYZ2xYLVBQQUxqOVZhaE9Zd3lIUkU5R0NqRjNDdGJ6dm1UbWZoa25INkRiWEJSc3I2N2dHM3RncmJyOE8zN2JTOHktdTFWY2RRVS1PbUhhcDBSLTBGNW5JMUYwLWF0SXd1WFhvWjFtWW5CSnUwWklkNHpibXpFdEIyLU04Mno1U3JRVGZWakdkRzl6cFVYbDZRd1NodWRTa3A5bjliLUkwYXpYdlh3LTRJenYzQ09wZWxHX0REMDNiU0R0dGpfa0doRmhnSjFuRjJkNUhiaHRTcVVfTkV0dVpBeWlOMVBGOU5weWZUSmwyRjJZWWxhY09BeURwTVAyNGQ2ZjVnSTY4LUkxbHFnUlNXUHpjRGQ4dTFjQWtoZHV1TmVxaGZzOGtDZ25Nclh6UF81RHJlcjlxbklidWZKUXgyWkhtWjN0LWc0VVFQYjdXQQ%3D%3D",
                    "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36,gzip(gfe)",
                    "clientName": "WEB",
                    "clientVersion": "2.20260811.07.00",
                    "osName": "X11",
                    "osVersion": "",
                    "originalUrl": "https://www.youtube.com/",
                    "platform": "DESKTOP",
                    "clientFormFactor": "UNKNOWN_FORM_FACTOR",
                    "windowWidthPoints": 1914,
                    "configInfo": {
                        "appInstallData": "CP_s9tMGEOn40RwQ4LfRHBD299EcEI6l0hwQibDOHBC0wdAcEAAQ8bTQHBCzkM8cEIKPzxwQofjQHBDgzbEFEIv3zxwQsZHRHBCe0LAFENeL0RwQpKnRHBD6qtIcEN68zhwQufDRHBDpqdEcEPyyzhwQzYi4IhC3-IATENr3zhwQuOTOHBCIkNEcEMOR0BwQsIbPHBDL0bEFEICD0hwQzN-uBRC9tq4FEKaasAUQpI7SHBD2q7AFEJqf0hwQvZmwBRDKk9IcEIOHuCIQt4bPHBCBzc4cELyk0BwQvoTRHBCkodIcEJmNsQUQrtbPHBDK-4ATEMb8gBMQ-5vSHBDn69EcEL6KsAUQtOCuBRCG4YATEM3RsQUQnYa4IhCukdIcENCIuCIQlofRHBDi1K4FEMf30RwQn8-AExDw3tEcEJCJuCIQy4i4IhDSvdAcEMGP0BwQyfaAExCHrM4cEPTp0RwqkAFDQU1TYUJWai1acS1ETWVVRXBVQ25BNzVGWjBGNFJhTTBBX1REZGdHNUFiWEFneUtCbGVsc3Q4TDhMRVNoMHd5b0t3RUE1Q3VBX3NtdHVRR2hSVDdvQVRwRTU1TGdpak0wZ0RMU3J5VEJOMllCc2ZHQlloYzJkVUYzU3psUm9OMmlXbTdVb2J5NGg3YkJoMEgwAA%3D%3D",
                        "coldConfigData": "CP_s9tMGEL22rgUQ4tSuBRDj-LAFEK-nzhwQ_LLOHBCwhs8cELOQzxwQntfPHBCahdAcEKiO0RwQsZHRHBDpqdEcEIe90RwQ9eHRHBD06dEcEJv-0RwQgYDSHBDwiNIcEOaP0hwQiZDSHBDKk9IcEKyV0hwQ_5XSHBCwmdIcEPmZ0hwQ_JnSHBC0m9IcELWb0hwQuJvSHBC6m9IcELyb0hwQxp7SHBCepNIcEKSq0hwQ-qrSHBDQiLgiEJCJuCIaMkFHbGVIVDBTaGwzRk5FZ2dzcTMxWmZ3TDFOZHp3azFUMEttSGtwODVDMDlrQzFXdm53IjJBR2xlSFQwU2hsM0ZORWdnc3EzMVpmd0wxTmR6d2sxVDBLbUhrcDg1QzA5a0MxV3Zudyq8AUNBTVNpQUVOTTdqZHR3S2tHZThweHphWmtwb1EteGFOTnY0ampSazA5aGoyTGM0Q21nVU1uQ1diQ285QnpRbjJFamY4QmE0ZTd4ZWdBVlVWVjZiZXRSLVJuQVhWeGdTVW5BVFB3Z0NQcHdiOTFBWXl6NEFGMmFRR0FfZjdCUE1EaU9RRjJJY0RwMC1ZRzdNR19yTUVoN3NHcXNFR3BxVVAtdFlGdGkzVlI2LVlCdUd2QnVDM0JZOEs3cjRH",
                        "coldHashData": "CP_s9tMGEhM0MjEwNzYyOTYzNDAyNjgzOTA0GP_s9tMGMjJBR2xlSFQwU2hsM0ZORWdnc3EzMVpmd0wxTmR6d2sxVDBLbUhrcDg1QzA5a0MxV3ZudzoyQUdsZUhUMFNobDNGTkVnZ3NxMzFaZndMMU5kendrMVQwS21Ia3A4NUMwOWtDMVd2bndCvAFDQU1TaUFFTk03amR0d0trR2U4cHh6YVprcG9RLXhhTk52NGpqUmswOWhqMkxjNENtZ1VNbkNXYkNvOUJ6UW4yRWpmOEJhNGU3eGVnQVZVVlY2YmV0Ui1SbkFYVnhnU1VuQVRQd2dDUHB3YjkxQVl5ejRBRjJhUUdBX2Y3QlBNRGlPUUYySWNEcDAtWUc3TUdfck1FaDdzR3FzRUdwcVVQLXRZRnRpM1ZSNi1ZQnVHdkJ1QzNCWThLN3I0Rw%3D%3D",
                        "hotHashData": "CP_s9tMGEhQxMDMxMDIyMzc1NzM5OTE5NTg3MRj_7PbTBiiU5PwSKKXQ_RIoyMr-Eii36v4SKJCbgBMo2LCAEyin2YATKMndgBMoxvyAEyjthYETKPmFgRMojoaBEyjCiYETMjJBR2xlSFQwU2hsM0ZORWdnc3EzMVpmd0wxTmR6d2sxVDBLbUhrcDg1QzA5a0MxV3ZudzoyQUdsZUhUMFNobDNGTkVnZ3NxMzFaZndMMU5kendrMVQwS21Ia3A4NUMwOWtDMVd2bndCNENBTVNJZzBKb3RmNkZhN0JCc2lfQnFFcXRRNFZGOTNQd2d5VmpRN2w4Zy1MRHJtUTN3cz0%3D",
                    },
                    "screenDensityFloat": 1,
                    "userInterfaceTheme": "USER_INTERFACE_THEME_LIGHT",
                    "timeZone": "Europe/Amsterdam",
                    "browserName": "Chrome",
                    "browserVersion": "151.0.0.0",
                    "memoryTotalKbytes": "4000000",
                    "acceptHeader": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "deviceExperimentId": "ChxOelkzTXpRNE9UazVPRE0xTmpRMU9UUTROZz09EP_s9tMGGP_s9tMG",
                    "rolloutToken": "CJKHgoO766SqQhCwqczPy52WAxiyy-TPy52WAw%3D%3D",
                    "screenWidthPoints": 1914,
                    "screenHeightPoints": 960,
                    "screenPixelDensity": 1,
                    "utcOffsetMinutes": 120,
                    "applicationState": "ACTIVE",
                    "connectionType": "CONN_CELLULAR_4G",
                    "mainAppWebInfo": {
                        "graftUrl": self.graft_url,
                        "pwaInstallabilityStatus": "PWA_INSTALLABILITY_STATUS_UNKNOWN",
                        "webDisplayMode": "WEB_DISPLAY_MODE_BROWSER",
                        "isWebNativeShareAvailable": False,
                    },
                },
                "user": {"lockedSafetyMode": False},
                "request": {"useSsl": True, "internalExperimentFlags": [], "consistencyTokenJars": []},
                "clickTracking": {"clickTrackingParams": tracking_param},
                "adSignalsInfo": {
                    "params": [
                        {"key": "dt", "value": "1786623616795"},
                        {"key": "flash", "value": "0"},
                        {"key": "frm", "value": "0"},
                        {"key": "u_tz", "value": "120"},
                        {"key": "u_his", "value": "5"},
                        {"key": "u_h", "value": "1080"},
                        {"key": "u_w", "value": "1920"},
                        {"key": "u_ah", "value": "1080"},
                        {"key": "u_aw", "value": "1920"},
                        {"key": "u_cd", "value": "24"},
                        {"key": "bc", "value": "31"},
                        {"key": "bih", "value": "960"},
                        {"key": "biw", "value": "1914"},
                        {"key": "brdim", "value": "0,0,0,0,1920,0,1920,1028,1914,960"},
                        {"key": "vis", "value": "1"},
                        {"key": "wgl", "value": "true"},
                        {"key": "ca_type", "value": "image"},
                    ]
                },
            },
            "continuation": continuation,
        }

    def download_continuation_json(self, continuation: str, tracking_param: str, index: int):
        DATARAW = self.get_data_raw(continuation=continuation, tracking_param=tracking_param)
        dataraw = json.dumps(DATARAW, allow_nan=False, check_circular=True, ensure_ascii=True)

        req = Request("https://www.youtube.com/youtubei/v1/browse?prettyPrint=false")
        req.add_header("content-type", "application/json")
        req.add_header("origin", "https://www.youtube.com")
        req.add_header(
            "user-agent",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
        )

        with urlopen(req, data=dataraw.encode()) as res:
            data = res.read()
            if isinstance(data, bytes):
                data = data.decode("utf-8")
                _logger.warning("Decoding data, res options are %s", dir(res))
        out_path = os.path.join(self._base_dir, f"out_{index}.txt")
        with open(out_path, "w") as f_out:
            f_out.write(data)

        return out_path

    def runloop(self, continuation: str, tracking_params: str):

        c, t = continuation, tracking_params

        index = 1
        while 1:
            print(index, c, t)
            out_path = self.download_continuation_json(c, t, index)
            with open(out_path, "r") as fp:
                data = json.load(fp=fp)

            ans = find_key_rec(data, "continuationCommand")
            if ans is None:
                break
            p, c2 = ans
            print(p)
            print(c2)
            # Get new token and trackingParams
            c = c2.get("token")
            t = data.get("trackingParams")

            assert c is not None
            index += 1
            time.sleep(self.wait_time)

    def download_page(self):

        with urlopen(self.graft_url, timeout=3000) as f:
            data = f.read()

        return data

    def retrieve_contiunationcommand_and_tracking_param_from_soup(self, soup):

        # step 1, download the PAGE, And get it into RAM
        # Step 2, extract the correct script definition
        scripts = soup.find_all("script")

        if not scripts:
            _logger.error("No Script found")
            return

        # YOLO to find the continuation command which ends in %3D%3D
        scripts = [x for x in scripts if x.text.startswith("var ytInitialData")]
        if not scripts:
            _logger.error("Non of the scripts define the variable ytInitialData")
        value = str(scripts[0].text.removesuffix(";").removeprefix("var ytInitialData = "))
        json_obj = json.loads(value)
        # Step 3 find and return the continuationCommand
        # command = json_obj
        command = find_key_rec(json_obj, "continuationCommand")[1]["token"]
        # for index in keys_to_continuation_token:
        # command = command[index]

        assert isinstance(command, str)

        trackingParams: str = json_obj["trackingParams"]
        assert isinstance(trackingParams, str)
        return command, trackingParams

    def run(self):

        html_data = self.download_page()
        soup = BeautifulSoup(html_data, features="html.parser")
        ans1 = self.retrieve_contiunationcommand_and_tracking_param_from_soup(soup=soup)
        if not ans1:
            _logger.error("No tokens found")
            return
        c, t = ans1

        print(c)
        print(t)
        self.runloop(c, t)


def main():
    c2ntinuation = "4qmFsgKBARIYVUNLeTFkQXFFTG8wenJPdFBrZjBlVE13GkxFZ1Z3YjNOMGM2b0RLQW9rVVRKb1ExSkdUWHBqUm14TlZrZDRTMVZxUWxkVE1VcEdZVWhDWVZKdGVFWlNWVVpDS0JUeUJnUUtBa29BmgIWYmFja3N0YWdlLWl0ZW0tc2VjdGlvbg%3D%3D"
    continuation = "4qmFsgKBARIYVUNLeTFkQXFFTG8wenJPdFBrZjBlVE13GkxFZ1Z3YjNOMGM2b0RLQW9rVVRKb1ExSkdWa2hqUkZacFlsWktUMVZxUWxkVlZrcEZVVlJTV0dKR1drUlNWVVpDS0FyeUJnUUtBa29BmgIWYmFja3N0YWdlLWl0ZW0tc2VjdGlvbg%3D%3D"
    tracking_param = "CCcQuy8YACITCOOa8dvLnZYDFWHCSQcdi_w6IMoBBDSTU08="
    graft_url = "https://www.youtube.com/@IGN/posts"
    parser = argparse.ArgumentParser()
    parser.add_argument("-P", "--directory-prefix", type=str)
    parser.add_argument("--wait-times", type=float, default=5)

    parser.add_argument("user")

    args = parser.parse_args()

    graft_url = f"https://www.youtube.com/@{args.user.strip().removeprefix('@')}/posts"
    directory_prefix = "."
    if not args.directory_prefix:
        directory_prefix = datetime.datetime.now().strftime("{}-%Y-%j").format(args.user)

    os.makedirs(directory_prefix, exist_ok=True)

    scraper = YtPostScraper(directory_prefix, graft_url, wait_time=args.wait_times)
    scraper.run()


if __name__ == "__main__":
    main()
