import json

import requests
import utils
from bs4 import BeautifulSoup


def download_insta_page(url, target):
    headers = [
        "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language: nl-NL,nl;q=0.9",
        "cache-control: no-cache",
        "dpr: 1",
        "pragma: no-cache",
        "priority: u=0, i",
        "referer: https://duckduckgo.com/",
        "sec-ch-prefers-color-scheme: light",
        'sec-ch-ua: "Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"',
        'sec-ch-ua-full-version-list: "Chromium";v="152.0.7977.64", "Not?A_Brand";v="24.0.0.0", "Google Chrome";v="152.0.7977.64"',
        "sec-ch-ua-mobile: ?0",
        'sec-ch-ua-model: ""',
        'sec-ch-ua-platform: "Linux"',
        'sec-ch-ua-platform-version: ""',
        "sec-fetch-dest: document",
        "sec-fetch-mode: navigate",
        "sec-fetch-site: same-origin",
        "sec-fetch-user: ?1",
        "upgrade-insecure-requests: 1",
        "user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
        "viewport-width: 1914",
    ]
    # headers = dict([tuple(h.decode("utf-8").rsplit(": ", 1)) for h in headers])
    x = [tuple(y) for y in [h.split(": ", 1) for h in headers] if len(y) == 2]
    print(x)
    print(headers)
    headers = dict(x)
    print(headers)

    res = requests.get(
        url=url,
        timeout=30000,
        data=None,
        headers=headers,
        json=None,
        allow_redirects=True,
        auth=None,
        cert=None,
        cookies=None,
        files=None,
        hooks=None,
        params=None,
        proxies=None,
        stream=None,
        verify=None,
    )
    data = res.content.decode("utf-8")
    print(data)
    with open(target, "w") as f:
        print(data, file=f)
    # curl --url  \
    #   -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
    #   -H 'accept-language: nl-NL,nl;q=0.9' \
    #   -H 'cache-control: no-cache' \
    #   -b 'csrftoken=knYXW4LbCkbA8xh3I6bj-D; datr=lSmDagjmqHEkJ2sAPpRNlC_N; ig_did=8B4D78DB-6FDC-4EF1-B49D-D6C255C6E7D4; mid=aoMplQAEAAFj9CdbeQW4NI0tmEZg; wd=1914x960' \
    #   -H 'dpr: 1' \
    #   -H 'pragma: no-cache' \
    #   -H 'priority: u=0, i' \
    #   -H 'referer: https://duckduckgo.com/' \
    #   -H 'sec-ch-prefers-color-scheme: light' \
    #   -H 'sec-ch-ua: "Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"' \
    #   -H 'sec-ch-ua-full-version-list: "Chromium";v="152.0.7977.64", "Not?A_Brand";v="24.0.0.0", "Google Chrome";v="152.0.7977.64"' \
    #   -H 'sec-ch-ua-mobile: ?0' \
    #   -H 'sec-ch-ua-model: ""' \
    #   -H 'sec-ch-ua-platform: "Linux"' \
    #   -H 'sec-ch-ua-platform-version: ""' \
    #   -H 'sec-fetch-dest: document' \
    #   -H 'sec-fetch-mode: navigate' \
    #   -H 'sec-fetch-site: same-origin' \
    #   -H 'sec-fetch-user: ?1' \
    #   -H 'upgrade-insecure-requests: 1' \
    #   -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36' \
    #   -H 'viewport-width: 1914'


def download_insta2():
    cookie = "csrftoken=knYXW4LbCkbA8xh3I6bj-D; datr=lSmDagjmqHEkJ2sAPpRNlC_N; ig_did=8B4D78DB-6FDC-4EF1-B49D-D6C255C6E7D4; mid=aoMplQAEAAFj9CdbeQW4NI0tmEZg; wd=1914x960"
    url = "https://www.instagram.com/api/graphql"
    headers = [
        "accept: */*",
        "accept-language: nl-NL,nl;q=0.9",
        "cache-control: no-cache",
        "content-type: application/x-www-form-urlencoded",
        "origin: https://www.instagram.com",
        "pragma: no-cache",
        "priority: u=1, i",
        "referer: https://www.instagram.com/miley/",
        "sec-ch-prefers-color-scheme: light",
        'sec-ch-ua: "Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"',
        'sec-ch-ua-full-version-list: "Chromium";v="152.0.7977.64", "Not?A_Brand";v="24.0.0.0", "Google Chrome";v="152.0.7977.64"',
        "sec-ch-ua-mobile: ?0",
        'sec-ch-ua-model: ""',
        'sec-ch-ua-platform: "Linux"',
        'sec-ch-ua-platform-version: ""',
        "sec-fetch-dest: empty",
        "sec-fetch-mode: cors",
        "sec-fetch-site: same-origin",
        "user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
        "x-asbd-id: 359341",
        "x-csrftoken: knYXW4LbCkbA8xh3I6bj-D",
        "x-fb-friendly-name: PolarisLoggedOutDesktopWWWProfilePostsTabContentQuery_connection",
        "x-fb-lsd: AdQGzW3iZZ7BFX8LN2qf8SvcUio",
        "x-ig-app-id: 936619743392459",
        "x-ig-max-touch-points: 10",
    ]
    data_raw = "av=0&__d=www&__user=0&__a=1&__req=o&__hs=20698.HYP%3Ainstagram_web_pkg.2.1...0&dpr=1&__ccg=EXCELLENT&__rev=1046611421&__s=cv7nzz%3Acqdfmc%3Aa5p711&__hsi=7680920097373117430&__dyn=7xeUjG1mxu1syaxG4Vp41twpUnwgU7SbzEdF8vyUco2qwJyE1kUhw2nVE4W0qa321Rw8G11wBz81s8hwGxu786a3a1YwBgao6C1uwoE2swlo8od8-U2zxe2GewGw9a361qw8Xxm16wa-0oa2-azo7u3C2u2J0bS1LyUaUbGxK3R08-269wr84-6o5p389oed6goK10xKi2K7E5y4U7a0EoKmUhw4rwXyEcFE461Hwj83KwRzk1jw&__csr=g9c5278YAW4Nal8I9hYYAlh4BsPmNsXtOiJj9WVCLXqCrlrqLtlOlA9syHrFSBl65BktjmGbRJvOiaJoyXYx4iCjyehQWAmJvY9T5_myZTUZmRUSgynFpdWAUCGoyiGQmDHBxi9ZxyiHX-8KfKdh9ESuKHxOqUjxy7E89pkrDK7pqx2dBCx64EOtau8BQi6AfAKunBByHQi2im4FXxqaCGl29oK5ouCynyoO2OHUjhEnwq64oy5E4V0KBG096oG0UE8o1jEng9U9kECEgDDwjbWK00zAE036swdK02gKcA8t010-bIE0hfw2L81BEG1KBg1YU4mzh0mglU1yE1-nwwEU4y6Ugw8R0Yy4kw5W1Ww2Wpo2jo0eJo0Zu014RCm10w2Zo42m0wo092o&__hsdp=giE5I4Iavn1t8y52kAyuVVlggucDiCzpojUwygBJ0MV16Et41GsqA2JyUiK7k1pwU83eQ0xO1TyA6oaUZio88iU6Kcw-w_xW0FQ78cUaUCm8wGwm87u0xU5e1gxG2e78K0MK5Q1lAw4Tw10q0P88ojw31o3fwTwmU0qnw9y1JwAw9y68K2qeho0L62O0gS8wqU1uVU0UK0qm0lG3m0ll3E8Q3h0hE96&__hblp=0i85W3y1AxW8x69h433wn8K2KdyVHz-m1oU8rh8iAz88o5610x-Vm6orByonwwghVUK4VQnwOz8fEfUuwsoCEa4dUO7olG2y9By8aE5y1MCBw-wgE5ecwgUqwzxObwbShwCz9U98Sim9xm0h60sa0A84W0K879od8bVE4u1dwioc80I20PUdU5K0fDw2v820wiE5Sfy8rxOm785y64ax658V5w8G09CwIw9W1Ky85e5U1uVU0UK0ME2cwlo5XwuE4S322qew-wio3cgW2d0Qg4q2hw&__sjsp=giE5I4Iarn6ggO8xgB9mqVVlggix-dBxfy292kh0UwiFNGgaUS4E06q2&__comet_req=7&lsd=AdQGzW3iZZ7BFX8LN2qf8SvcUio&jazoest=22273&__spin_r=1046611421&__spin_b=trunk&__spin_t=1788353570&__crn=comet.igweb.PolarisLoggedOutDesktopWWWProfileRoute&fb_api_caller_class=RelayModern&fb_api_req_friendly_name=PolarisLoggedOutDesktopWWWProfilePostsTabContentQuery_connection&server_timestamps=true&variables=%7B%22after%22%3A%22AQHTRenDqNolYSQatLAlV0uL2-oQ_L7fJ3f_0AuXvVxE9s-3n7HrP3h3WBkCDNZo-AMffCFOxi3dvJ7QSA4IiqABCQ%22%2C%22first%22%3A12%2C%22id%22%3A%2217841401148975089%22%7D&doc_id=27389614800735091"

    data_ra1 = "av=0&__d=www&__user=0&__a=1&__req=21&__hs=20698.HYP%3Ainstagram_web_pkg.2.1...0&dpr=1&__ccg=EXCELLENT&__rev=1046611421&__s=fjuia1%3Acqdfmc%3Aa5p711&__hsi=7680920097373117430&__dyn=7xeUjG1mxu1syaxG4Vp41twpUnwgU7SbzEdF8vyUco2qwJyE1kUhw2nVE4W0qa321Rw8G11wBz81s8hwGxu786a3a1YwBgao6C1uwoE2swlo8od8-U2zxe2GewGw9a361qw8Xxm16wa-0oa2-azo7u3C2u2J0bS1LyUaUbGxK3R08-269wr84-6o5p389oed6goK10xKi2K7E5y4U7a0EoKmUhw4rwXyEcFE461Hwj83KwRzk1jw&__csr=g9c5278YAW4Nal8I9hYYAlh4BsPmNsXtOiJj9WVCLXqCrlrqLtlOlA9syHrFSBl65BktjmGbRJvOiaJoyXYx4iCjyehQWAmJvY9T5_myZTUZmRUSgynFpdWAUCGoyiGQmDHBxi9ZxyiHX-8KfKdh9ESuKHxOqUjxy7E89pkrDK7pqx2dBCx64EOtau8BQi6AfAKunBByHQi2im4FXxqaCGl29oK5ouCynyoO2OHUjhEnwq64oy5E4V0KBG096oG0UE8o1jEng9U9kECEgDDwjbWK00zAE036swdK02gKcA8t010-bIE0hfw2L81BEG1KBg1YU4mzh0mglU1yE1-nwwEU4y6Ugw8R0Yy4kw5W1Ww2Wpo2jo0eJo0Zu014RCm10w2Zo42m0wo092o&__hsdp=giE5I4Iavn1t8y52kAyuVVlggucDiCzpojUwygBJ0MV16Et41GsqA2JyUiK7k1pwU83eQ0xO1TyA6oaUZio88iU6Kcw-w_xW0FQ78cUaUCm8wGwm87u0xU5e1gxG2e78K0MK5Q1lAw4Tw10q0P88ojw31o3fwTwmU0qnw9y1JwAw9y68K2qeho0L62O0gS8wqU1uVU0UK0qm0lG3m0ll3E8Q3h0hE96&__hblp=0i85W3y1AxW8x69h433wn8K2KdyVHz-m1oU8rh8iAz88o5610x-Vm6orByonwwghVUK4VQnwOz8fEfUuwsoCEa4dUO7olG2y9By8aE5y1MCBw-wgE5ecwgUqwzxObwbShwCz9U98Sim9xm0h60sa0A84W0K879od8bVE4u1dwioc80I20PUdU5K0fDw2v820wiE5Sfy8rxOm785y64ax658V5w8G09CwIw9W1Ky85e5U1uVU0UK0ME2cwlo5XwuE4S322qew-wio3cgW2d0Qg4q2hw&__sjsp=giE5I4Iarn6ggO8xgB9mqVVlggix-dBxfy292kh0UwiFNGgaUS4E06q2&__comet_req=7&lsd=AdQGzW3iZZ7BFX8LN2qf8SvcUio&jazoest=22273&__spin_r=1046611421&__spin_b=trunk&__spin_t=1788353570&__crn=comet.igweb.PolarisLoggedOutDesktopWWWProfileRoute&fb_api_caller_class=RelayModern&fb_api_req_friendly_name=PolarisLoggedOutDesktopWWWProfilePostsTabContentQuery_connection&server_timestamps=true&variables=%7B%22after%22%3A%22AQHT_VS5NxrsraO7Ohn2nZGS7S0YPqZQ5Jn8Di7WftNv98MUktp2VSS87nDypeSi6VRXjJ5Pkjdm7eklBwA-g8Xz0g%22%2C%22first%22%3A12%2C%22id%22%3A%2217841401148975089%22%7D&doc_id=27389614800735091"

    data_ra2 = "av=0&__d=www&__user=0&__a=1&__req=2b&__hs=20698.HYP%3Ainstagram_web_pkg.2.1...0&dpr=1&__ccg=EXCELLENT&__rev=1046611421&__s=fjuia1%3Acqdfmc%3Aa5p711&__hsi=7680920097373117430&__dyn=7xeUjG1mxu1syaxG4Vp41twpUnwgU7SbzEdF8vyUco2qwJyE1kUhw2nVE4W0qa321Rw8G11wBz81s8hwGxu786a3a1YwBgao6C1uwoE2swlo8od8-U2zxe2GewGw9a361qw8Xxm16wa-0oa2-azo7u3C2u2J0bS1LyUaUbGxK3R08-269wr84-6o5p389oed6goK10xKi2K7E5y4U7a0EoKmUhw4rwXyEcFE461Hwj83KwRzk1jw&__csr=g9c5278YAW4Nal8I9hYYAlh4BsPmNsXtOiJj9WVCLXqCrlrqLtlOlA9syHrFSBl65BktjmGbRJvOiaJoyXYx4iCjyehQWAmJvY9T5_myZTUZmRUSgynFpdWAUCGoyiGQmDHBxi9ZxyiHX-8KfKdh9ESuKHxOqUjxy7E89pkrDK7pqx2dBCx64EOtau8BQi6AfAKunBByHQi2im4FXxqaCGl29oK5ouCynyoO2OHUjhEnwq64oy5E4V0KBG096oG0UE8o1jEng9U9kECEgDDwjbWK00zAE036swdK02gKcA8t010-bIE0hfw2L81BEG1KBg1YU4mzh0mglU1yE1-nwwEU4y6Ugw8R0Yy4kw5W1Ww2Wpo2jo0eJo0Zu014RCm10w2Zo42m0wo092o&__hsdp=giE5I4Iavn1t8y52kAyuVVlggucDiCzpojUwygBJ0MV16Et41GsqA2JyUiK7k1pwU83eQ0xO1TyA6oaUZio88iU6Kcw-w_xW0FQ78cUaUCm8wGwm87u0xU5e1gxG2e78K0MK5Q1lAw4Tw10q0P88ojw31o3fwTwmU0qnw9y1JwAw9y68K2qeho0L62O0gS8wqU1uVU0UK0qm0lG3m0ll3E8Q3h0hE96&__hblp=0i85W3y1AxW8x69h433wn8K2KdyVHz-m1oU8rh8iAz88o5610x-Vm6orByonwwghVUK4VQnwOz8fEfUuwsoCEa4dUO7olG2y9By8aE5y1MCBw-wgE5ecwgUqwzxObwbShwCz9U98Sim9xm0h60sa0A84W0K879od8bVE4u1dwioc80I20PUdU5K0fDw2v820wiE5Sfy8rxOm785y64ax658V5w8G09CwIw9W1Ky85e5U1uVU0UK0ME2cwlo5XwuE4S322qew-wio3cgW2d0Qg4q2hw&__sjsp=giE5I4Iarn6ggO8xgB9mqVVlggix-dBxfy292kh0UwiFNGgaUS4E06q2&__comet_req=7&lsd=AdQGzW3iZZ7BFX8LN2qf8SvcUio&jazoest=22273&__spin_r=1046611421&__spin_b=trunk&__spin_t=1788353570&__crn=comet.igweb.PolarisLoggedOutDesktopWWWProfileRoute&fb_api_caller_class=RelayModern&fb_api_req_friendly_name=PolarisLoggedOutDesktopWWWProfilePostsTabContentQuery_connection&server_timestamps=true&variables=%7B%22after%22%3A%22AQHTj5c0hHLxTWHo_wLS8t3FaXX-VrYFcobAAVXQQBMFan1AQ7AMkY9tgyiMlqAbdJVzsdd5n4F_ybtcqJRrqL01Dw%22%2C%22first%22%3A12%2C%22id%22%3A%2217841401148975089%22%7D&doc_id=27389614800735091"

    headers = dict([tuple(x.split(": ", 1)) for x in headers])

    res = requests.post(url=url, cookies=None, headers=headers, allow_redirects=True, data=data_raw)

    target = "insta_url_1.json"
    with open(target, "xb") as f:
        f.write(res.content)

    return target
    # curl --url 'https://www.instagram.com/api/graphql' \
    #   -H 'accept: */*' \
    #   -H 'accept-language: nl-NL,nl;q=0.9' \
    #   -H 'cache-control: no-cache' \
    #   -H 'content-type: application/x-www-form-urlencoded' \
    #   -b 'csrftoken=knYXW4LbCkbA8xh3I6bj-D; datr=lSmDagjmqHEkJ2sAPpRNlC_N; ig_did=8B4D78DB-6FDC-4EF1-B49D-D6C255C6E7D4; mid=aoMplQAEAAFj9CdbeQW4NI0tmEZg; wd=1914x960' \
    #   -H 'origin: https://www.instagram.com' \
    #   -H 'pragma: no-cache' \
    #   -H 'priority: u=1, i' \
    #   -H 'referer: https://www.instagram.com/miley/' \
    #   -H 'sec-ch-prefers-color-scheme: light' \
    #   -H 'sec-ch-ua: "Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"' \
    #   -H 'sec-ch-ua-full-version-list: "Chromium";v="152.0.7977.64", "Not?A_Brand";v="24.0.0.0", "Google Chrome";v="152.0.7977.64"' \
    #   -H 'sec-ch-ua-mobile: ?0' \
    #   -H 'sec-ch-ua-model: ""' \
    #   -H 'sec-ch-ua-platform: "Linux"' \
    #   -H 'sec-ch-ua-platform-version: ""' \
    #   -H 'sec-fetch-dest: empty' \
    #   -H 'sec-fetch-mode: cors' \
    #   -H 'sec-fetch-site: same-origin' \
    #   -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36' \
    #   -H 'x-asbd-id: 359341' \
    #   -H 'x-csrftoken: knYXW4LbCkbA8xh3I6bj-D' \
    #   -H 'x-fb-friendly-name: PolarisLoggedOutDesktopWWWProfilePostsTabContentQuery_connection' \
    #   -H 'x-fb-lsd: AdQGzW3iZZ7BFX8LN2qf8SvcUio' \
    #   -H 'x-ig-app-id: 936619743392459' \
    #   -H 'x-ig-max-touch-points: 10' \
    #   --data-raw 'av=0&__d=www&__user=0&__a=1&__req=o&__hs=20698.HYP%3Ainstagram_web_pkg.2.1...0&dpr=1&__ccg=EXCELLENT&__rev=1046611421&__s=cv7nzz%3Acqdfmc%3Aa5p711&__hsi=7680920097373117430&__dyn=7xeUjG1mxu1syaxG4Vp41twpUnwgU7SbzEdF8vyUco2qwJyE1kUhw2nVE4W0qa321Rw8G11wBz81s8hwGxu786a3a1YwBgao6C1uwoE2swlo8od8-U2zxe2GewGw9a361qw8Xxm16wa-0oa2-azo7u3C2u2J0bS1LyUaUbGxK3R08-269wr84-6o5p389oed6goK10xKi2K7E5y4U7a0EoKmUhw4rwXyEcFE461Hwj83KwRzk1jw&__csr=g9c5278YAW4Nal8I9hYYAlh4BsPmNsXtOiJj9WVCLXqCrlrqLtlOlA9syHrFSBl65BktjmGbRJvOiaJoyXYx4iCjyehQWAmJvY9T5_myZTUZmRUSgynFpdWAUCGoyiGQmDHBxi9ZxyiHX-8KfKdh9ESuKHxOqUjxy7E89pkrDK7pqx2dBCx64EOtau8BQi6AfAKunBByHQi2im4FXxqaCGl29oK5ouCynyoO2OHUjhEnwq64oy5E4V0KBG096oG0UE8o1jEng9U9kECEgDDwjbWK00zAE036swdK02gKcA8t010-bIE0hfw2L81BEG1KBg1YU4mzh0mglU1yE1-nwwEU4y6Ugw8R0Yy4kw5W1Ww2Wpo2jo0eJo0Zu014RCm10w2Zo42m0wo092o&__hsdp=giE5I4Iavn1t8y52kAyuVVlggucDiCzpojUwygBJ0MV16Et41GsqA2JyUiK7k1pwU83eQ0xO1TyA6oaUZio88iU6Kcw-w_xW0FQ78cUaUCm8wGwm87u0xU5e1gxG2e78K0MK5Q1lAw4Tw10q0P88ojw31o3fwTwmU0qnw9y1JwAw9y68K2qeho0L62O0gS8wqU1uVU0UK0qm0lG3m0ll3E8Q3h0hE96&__hblp=0i85W3y1AxW8x69h433wn8K2KdyVHz-m1oU8rh8iAz88o5610x-Vm6orByonwwghVUK4VQnwOz8fEfUuwsoCEa4dUO7olG2y9By8aE5y1MCBw-wgE5ecwgUqwzxObwbShwCz9U98Sim9xm0h60sa0A84W0K879od8bVE4u1dwioc80I20PUdU5K0fDw2v820wiE5Sfy8rxOm785y64ax658V5w8G09CwIw9W1Ky85e5U1uVU0UK0ME2cwlo5XwuE4S322qew-wio3cgW2d0Qg4q2hw&__sjsp=giE5I4Iarn6ggO8xgB9mqVVlggix-dBxfy292kh0UwiFNGgaUS4E06q2&__comet_req=7&lsd=AdQGzW3iZZ7BFX8LN2qf8SvcUio&jazoest=22273&__spin_r=1046611421&__spin_b=trunk&__spin_t=1788353570&__crn=comet.igweb.PolarisLoggedOutDesktopWWWProfileRoute&fb_api_caller_class=RelayModern&fb_api_req_friendly_name=PolarisLoggedOutDesktopWWWProfilePostsTabContentQuery_connection&server_timestamps=true&variables=%7B%22after%22%3A%22AQHTRenDqNolYSQatLAlV0uL2-oQ_L7fJ3f_0AuXvVxE9s-3n7HrP3h3WBkCDNZo-AMffCFOxi3dvJ7QSA4IiqABCQ%22%2C%22first%22%3A12%2C%22id%22%3A%2217841401148975089%22%7D&doc_id=27389614800735091'


def scrape_loop(*, save_html=False, save_json=False, save_urls=False):
    first = "insta_url_1.json"
    with open(first, "r") as f:
        data = json.load(fp=f)

    print(data)

    display_uris = utils.find_keys_rec(data, "display_uri", with_path=False)
    print(*display_uris, sep="\n")


def scrape_initial(*, save_html=False, save_json=False, save_urls=False):

    url = "https://www.instagram.com/reel/DOilkhCk4sv"
    target = "temp__2.html"

    # download_insta_page(url,target)

    with open(target, "r") as f:
        data = f.read()

    soup = BeautifulSoup(data, features="html.parser")

    # print(soup)

    scripts = soup.find_all("script")
    print(len(scripts))
    target_script = find_target_script(scripts)
    print(len(str(target_script)))
    print(type(target_script))
    print(dir(target_script))

    x = json.loads(target_script.text)
    print(x)
    p = utils.find_keys_rec(x, "display_uri", with_path=True)
    for a, b in p:
        print(a, b)

    # find it wihtout utils
    p = x["require"][0][3][0]["__bbox"]["require"][5][3][1]["__bbox"]["result"]["data"]["xig_polaris_media"][
        "if_not_gated_logged_out"
    ]["user"]["polaris_ordered_timeline_connection"]["edges"]

    for d in p:
        with open("urls.txt", "a") if save_urls else MockFile() as f:
            print(d["node"]["display_uri"], file=f)


class MockFile:
    def __enter__(self):
        pass

    def __exit__(self, a, b, c):
        pass


def find_target_script(scripts):
    for i, s in enumerate(scripts):
        # print(i, str(s)[:75])
        if "display_uri" in s.text:
            # print(i, str(s)[:75])
            return s


def main():

    from argparse import ArgumentParser, BooleanOptionalAction

    parser = ArgumentParser()

    parser.add_argument("--save-html", action=BooleanOptionalAction, default=True)
    parser.add_argument("--save-json", action=BooleanOptionalAction, default=True)
    parser.add_argument("--save-urls", action=BooleanOptionalAction, default=True)
    args = parser.parse_args()

    # scrape(save_html=args.save_html, save_json=args.save_json, save_urls=args.save_urls)
    # download_insta2()
    scrape_loop()
    # download_insta_page(url)


if __name__ == "__main__":
    main()
