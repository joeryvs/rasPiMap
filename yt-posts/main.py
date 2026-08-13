import argparse
import io
import json
import multiprocessing
import os
import pathlib
import subprocess
import sys
import threading
import time
from typing import Any


class YtPostScraper:
    def __init__(self, base_dir, graft_url) -> None:
        self._base_dir = base_dir
        self.graft_url = graft_url

        assert os.path.exists(self._base_dir) and os.path.isdir(self._base_dir), (
            "Scraping store directory does not exist"
        )

    def get_data_raw(self, continuation, tracking_param):
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

    def run_curl_command2(self, continuation, tracking_param, index=0):
        DATARAW = self.get_data_raw(continuation=continuation, tracking_param=tracking_param)
        dataraw = json.dumps(DATARAW, allow_nan=False, check_circular=True, ensure_ascii=True)
        args = [
            "curl",
            "--url",
            "https://www.youtube.com/youtubei/v1/browse?prettyPrint=false",
            "-H",
            "content-type: application/json",
            "-H",
            "origin: https://www.youtube.com",
            "-H",
            "user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
            # "-b",
            # "YSC=L1QSODVcqb8; PREF=tz=Europe.Amsterdam; SOCS=CAISEwgDEgk5NjMxMDU5OTgaAm5sIAEaBgiAkvTTBg; VISITOR_INFO1_LIVE=oLwvk0UT5P0; VISITOR_PRIVACY_METADATA=CgJOTBIiEh4SHAsMDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicgIw%3D%3D; __Secure-YNID=20.YT=T79a7URVGMA19XglX-PPALj9VahOYwyHRE9GCjF3CtbzvmTmfhknH6DbXBRsr67gG3tgrbr8O37bS8y-u1VcdQU-OmHap0R-0F5nI1F0-atIwuXXoZ1mYnBJu0ZId4zbmzEtB2-M82z5SrQTfVjGdG9zpUXl6QwShudSkp9n9b-I0azXvXw-4Izv3COpelG_DD03bSDttj_kGhFhgJ1nF2d5HbhtSqU_NEtuZAyiN1PF9NpyfTJl2F2YYlacOAyDpMP24d6f5gI68-I1lqgRSWPzcDd8u1cAkhduuNeqhfs8kCgnMrXzP_5Drer9qnIbufJQx2ZHmZ3t-g4UQPb7WA; GPS=1; __Secure-ROLLOUT_TOKEN=CJKHgoO766SqQhCwqczPy52WAxiyy-TPy52WAw%3D%3D; ST-1vpkvfn=itct=CCUQ8JMBGAsiEwjP_ujZy52WAxUCd3oFHU9AGC3KAQQ0k1NP&csn=MuNdyR90q1h2JPTE&endpoint=%7B%22clickTrackingParams%22%3A%22CCUQ8JMBGAsiEwjP_ujZy52WAxUCd3oFHU9AGC3KAQQ0k1NP%22%2C%22commandMetadata%22%3A%7B%22webCommandMetadata%22%3A%7B%22url%22%3A%22%2F%40IGN%2Fposts%22%2C%22webPageType%22%3A%22WEB_PAGE_TYPE_CHANNEL%22%2C%22rootVe%22%3A3611%2C%22apiUrl%22%3A%22%2Fyoutubei%2Fv1%2Fbrowse%22%7D%7D%2C%22browseEndpoint%22%3A%7B%22browseId%22%3A%22UCKy1dAqELo0zrOtPkf0eTMw%22%2C%22params%22%3A%22EgVwb3N0c_IGBAoCSgA%253D%22%2C%22canonicalBaseUrl%22%3A%22%2F%40IGN%22%7D%7D",
            "--data-raw",
            dataraw,
        ]
        out_path = os.path.join(self._base_dir, f"out_{index}.txt")
        err_path = os.path.join(self._base_dir, f"err_{index}.txt")
        with open(out_path, "w") as f_out, open(err_path, "w") as f_err:
            subprocess.run(args=args, check=True, stdout=f_out, stderr=f_err)

        return out_path

    def runloop(self, continuation, tracking_params):

        c, t = continuation, tracking_params

        index = 1
        while 1:
            print(index, c, t)
            out_path = self.run_curl_command2(c, t, index)
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
            input()

            assert c is not None
            index += 1
            time.sleep(3)
            print(data)
            time.sleep(2)

    def download_main_page(self):

        args = ["curl", "--url", self.graft_url]

        subprocess.run(args, check=True)


def run(input_file, output_file):

    with open(input_file, "r") as f:
        data = json.load(fp=f)
    print(data)

    with open(output_file, "w") as f:
        json.dump(obj=data, fp=f, allow_nan=False, check_circular=True, indent=2)


def find_key_rec(obj, key):
    SENTINAL = object()

    def find_key_rec2(obj) -> None | tuple[list[str | int], Any]:
        if isinstance(obj, dict):
            if key in obj:
                return [], (obj.get(key, SENTINAL) or SENTINAL)

            for k, v in obj.items():
                if (answer := find_key_rec2(v)) is not None:
                    p, a = answer
                    return ([k] + p), a

        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                if (answer := find_key_rec2(v)) is not None:
                    p, a = answer
                    return ([i] + p), a
        return None

    return find_key_rec2(obj=obj)


def main():
    c2ntinuation = "4qmFsgKBARIYVUNLeTFkQXFFTG8wenJPdFBrZjBlVE13GkxFZ1Z3YjNOMGM2b0RLQW9rVVRKb1ExSkdUWHBqUm14TlZrZDRTMVZxUWxkVE1VcEdZVWhDWVZKdGVFWlNWVVpDS0JUeUJnUUtBa29BmgIWYmFja3N0YWdlLWl0ZW0tc2VjdGlvbg%3D%3D"
    continuation = "4qmFsgKBARIYVUNLeTFkQXFFTG8wenJPdFBrZjBlVE13GkxFZ1Z3YjNOMGM2b0RLQW9rVVRKb1ExSkdWa2hqUkZacFlsWktUMVZxUWxkVlZrcEZVVlJTV0dKR1drUlNWVVpDS0FyeUJnUUtBa29BmgIWYmFja3N0YWdlLWl0ZW0tc2VjdGlvbg%3D%3D"
    tracking_param = "CCcQuy8YACITCOOa8dvLnZYDFWHCSQcdi_w6IMoBBDSTU08="
    graft_url = "https://www.youtube.com/@IGN/posts"
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", type=pathlib.Path, required=True)
    parser.add_argument("-o", "--output-file", type=pathlib.Path, required=True)
    parser.add_argument("-P", "--directory-prefix", type=str, default=".")
    parser.add_argument("graft-url", required=False)

    args = parser.parse_args()
    if args.graft_url:
        graft_url = f"https://www.youtube.com/@{args.graft_url.strip().removeprefix('@')}/posts"

    os.makedirs(args.directory_prefix, exist_ok=True)

    scraper = YtPostScraper(args.directory_prefix, graft_url)
    # scraper.run_curl_command2(continuation=continuation, tracking_param=tracking_param)
    scraper.runloop(continuation=continuation, tracking_params=tracking_param)


if __name__ == "__main__":
    main()
