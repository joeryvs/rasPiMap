#!/usr/bin/env python
"""
Download utility as an easy way to get file from the net

  python -m wget <URL>
  python wget.py <URL>

Downloads: http://pypi.python.org/pypi/wget/
Development: http://bitbucket.org/techtonik/python-wget/

wget.py is not option compatible with Unix wget utility,
to make command line interface intuitive for new people.

Public domain by anatoly techtonik <techtonik@gmail.com>
Also available under the terms of MIT license
Copyright (c) 2010-2015 anatoly techtonik
"""

__version__ = "1.0"


import logging
import math
import os
import random
import sys
import time
import urllib.parse as urlparse

import requests

DEFAULT_TIMEOUT = 6000
_logger = logging.getLogger(__name__)

# --- workarounds for Python misbehavior ---

# --- helpers ---


def pause_execution(seconds, random_wait: bool = False):
    if random_wait:
        seconds = max(0, seconds + random.uniform(-0.5, 0.5))
    return time.sleep(seconds)


def _to_unicode(filename: str) -> str:
    """:return: filename decoded from utf-8 to unicode"""
    return filename


def _filename_from_url(url: str) -> str | None:
    """:return: detected filename as unicode or None"""
    # [ ] test urlparse behavior with unicode url
    fname = os.path.basename(urlparse.urlparse(url).path)
    if len(fname.strip(" \n\t.")) == 0:
        return None
    return _to_unicode(fname)


def _filename_from_headers(headers: dict | list | str) -> str | None:
    """Detect filename from Content-Disposition headers if present.
    http://greenbytes.de/tech/tc2231/

    :param: headers as dict, list or string
    :return: filename from content-disposition header or None
    """
    if isinstance(headers, str):
        headers = headers.splitlines()
    if isinstance(headers, list):
        headers = dict([x.split(":", 1) for x in headers])
    cdisp = headers.get("Content-Disposition")
    if not cdisp:
        return None
    cdtype = cdisp.split(";")
    if len(cdtype) == 1:
        return None
    if cdtype[0].strip().lower() not in ("inline", "attachment"):
        return None
    # several filename params is illegal, but just in case
    fnames = [x for x in cdtype[1:] if x.strip().startswith("filename=")]
    if len(fnames) > 1:
        return None
    name = fnames[0].split("=")[1].strip(' \t"')
    name = os.path.basename(name)
    if not name:
        return None
    return name


def _filename_fix_existing(filename: str) -> str:
    """Expands name portion of filename with numeric ' (x)' suffix to
    return filename that doesn't exist already.
    """
    dirname = "."
    name, ext = filename.rsplit(".", 1)
    names = [x for x in os.listdir(dirname) if x.startswith(name)]
    names = [x.rsplit(".", 1)[0] for x in names]
    suffixes = [x.replace(name, "") for x in names]
    # filter suffixes that match ' (x)' pattern
    suffixes = [x[2:-1] for x in suffixes if x.startswith(" (") and x.endswith(")")]
    indexes = [int(x) for x in suffixes if set(x) <= set("0123456789")]
    idx = 1
    if indexes:
        idx += max(indexes)
    return "%s (%d).%s" % (name, idx, ext)


# --- terminal/console output helpers ---


def _get_console_width():
    """Return width of available window area. Autodetection works for
    Windows and POSIX platforms. Returns 80 for others

    Code from http://bitbucket.org/techtonik/python-pager
    """
    if os.name == "posix":
        from array import array
        from fcntl import ioctl
        from termios import TIOCGWINSZ

        winsize = array("H", [0] * 4)
        try:
            ioctl(sys.stdout.fileno(), TIOCGWINSZ, winsize)
        except IOError:
            pass
        return (winsize[1], winsize[0])[0]

    return 80


def _bar_thermometer(current: int, total: int, width: int = 80) -> str:
    """Return thermometer style progress bar string. `total` argument
    can not be zero. The minimum size of bar returned is 3. Example:

        [..........            ]

    Control and trailing symbols (\r and spaces) are not included.
    See `bar_adaptive` for more information.
    """
    # number of dots on thermometer scale
    avail_dots = width - 2
    shaded_dots = math.floor(float(current) / total * avail_dots)
    return "[" + "." * shaded_dots + " " * (avail_dots - shaded_dots) + "]"


def _bar_adaptive(current: int, total: int, width: int = 80) -> str:
    """Return progress bar string for given values in one of three
    styles depending on available width:

        [..  ] downloaded / total
        downloaded / total
        [.. ]

    if total value is unknown or <= 0, show bytes counter using two
    adaptive styles:

        %s / unknown
        %s

    if there is not enough space on the screen, do not display anything

    returned string doesn't include control characters like \r used to
    place cursor at the beginning of the line to erase previous content.

    this function leaves one free character at the end of string to
    avoid automatic linefeed on Windows.
    """

    # process special case when total size is unknown and return immediately
    if not total or total < 0:
        msg = "%s / unknown" % current
        if len(msg) < width:  # leaves one character to avoid linefeed
            return msg
        if len("%s" % current) < width:
            return "%s" % current

    # --- adaptive layout algorithm ---
    #
    # [x] describe the format of the progress bar
    # [x] describe min width for each data field
    # [x] set priorities for each element
    # [x] select elements to be shown
    #   [x] choose top priority element min_width < avail_width
    #   [x] lessen avail_width by value if min_width
    #   [x] exclude element from priority list and repeat

    #  10% [.. ]  10/100
    # pppp bbbbb sssssss

    min_width = {
        "percent": 4,  # 100%
        "bar": 3,  # [.]
        "size": len("%s" % total) * 2 + 3,  # 'xxxx / yyyy'
    }
    priority = ["percent", "bar", "size"]

    # select elements to show
    selected = []
    avail = width
    for field in priority:
        if min_width[field] < avail:
            selected.append(field)
            avail -= min_width[field] + 1  # +1 is for separator or for reserved space at
            # the end of line to avoid linefeed on Windows
    # render
    output = ""
    for field in selected:
        if field == "percent":
            # fixed size width for percentage
            output += ("%s%%" % (100 * current // total)).rjust(min_width["percent"])
        elif field == "bar":  # [. ]
            # bar takes its min width + all available space
            output += _bar_thermometer(current, total, min_width["bar"] + avail)
        elif field == "size":
            # size field has a constant width (min == max)
            output += ("%s / %s" % (current, total)).rjust(min_width["size"])

        selected = selected[1:]
        if selected:
            output += " "  # add field separator

    return output


# --/ console helpers


def _detect_filename(url=None, out=None, headers=None, default="download.wget"):
    """Return filename for saving file. If no filename is detected from output
    argument, url or headers, return default (download.wget)
    """
    names = dict(out="", url="", headers="")
    if out:
        names["out"] = out or ""
    if url:
        names["url"] = _filename_from_url(url) or ""
    if headers:
        names["headers"] = _filename_from_headers(headers) or ""
    return names["out"] or names["headers"] or names["url"] or default


def curl_download(url: str, output_file: str):
    # download 1 file, and output it, simulating a single curl call
    _logger.debug("Download %s, saving to %s", url, output_file)
    with requests.get(url=url, timeout=DEFAULT_TIMEOUT) as res, open(output_file, "wb") as f:
        f.write(res.content)


def download_file(url, out=None):
    """High level function, which downloads URL into tmp file in current
    directory and then renames it to filename autodetected from either URL
    or HTTP headers.

    :param out: output filename or directory
    :return:    filename where URL is downloaded to
    """
    # detect if out is a directory
    outdir = None
    if out and os.path.isdir(out):
        outdir = out
        out = None

    with requests.get(url=url, timeout=DEFAULT_TIMEOUT) as res:
        headers = res.headers
        filename = _detect_filename(url, out, headers)
        if outdir:
            filename = os.path.join(outdir, filename)
        # add numeric ' (x)' suffix if filename already exists
        if os.path.exists(filename):
            filename = _filename_fix_existing(filename)
        with open(filename, "xb") as f:
            f.write(res.content)
        _logger.info("saving %s to %s", res.url, filename)
    # print headers
    return filename


def download_from_stream(urls, directory_prefix: str, *, wait_time: float = 0, random_wait=False):
    """High level function, which downloads URLS from a stream, into directory
    renames it to filename autodetected from either URL or HTTP headers.

    :param directory_prefix: output filename or directory
    :param wait_time: amount of time to wait between requests
    :param random_wait: boolean flag to fluctuate wait time
    :return:    status_code
    """
    status_code = 0
    rejected = []
    with requests.Session() as session:
        for i, url in enumerate(urls):
            if i and wait_time >= 0:
                pause_execution(wait_time, random_wait)
            try:
                with session.get(url=url, timeout=DEFAULT_TIMEOUT) as res:
                    headers = res.headers
                    filename = _detect_filename(url, None, headers)

                    filename = os.path.join(directory_prefix, filename)

                    # add numeric ' (x)' suffix if filename already exists
                    if os.path.exists(filename):
                        filename = _filename_fix_existing(filename)
                    # Create the directory prefix directory if it does not exists yet
                    os.makedirs(directory_prefix, exist_ok=True)
                    # write content
                    with open(filename, "xb") as f:
                        f.write(res.content)
                    _logger.info("[%s] saving %s to %s", i, res.url, filename)
            except requests.exceptions.RequestException as e:
                _logger.error("connection error for %s, %s", url, e.filename)
                rejected.append((url, e))
    return status_code


def download_from_file(input_file, directory_prefix: str, *, wait_time: float = 0, random_wait: bool = False):

    with open(input_file, "r") as f:
        return download_from_stream(
            [x.strip() for x in f], directory_prefix=directory_prefix, wait_time=wait_time, random_wait=random_wait
        )


usage = """\
usage: wget.py [options] URL

options:
  -o --output FILE|DIR   output filename or directory
  -h --help
  --version
"""


def main():
    # from optparse import OptionParser
    from argparse import ArgumentParser, BooleanOptionalAction

    parser = ArgumentParser(add_help=True)

    parser.add_argument("-V", "--version", action="version", version=__version__)

    parser.add_argument("url")
    parser.add_argument(
        "-b",
        "--background",
        help="Go  to  background immediately after startup.  If no output file is specified via the -o, output is redirected to wget-log.",
    )
    parser.add_argument(
        "-e",
        "--execute",
        help="Execute command as if it were a part of .wgetrc.   A  command  thus invoked will be executed after the commands in .wgetrc, thus taking precedence  over them.  If you need to specify more than one wgetrc               command, use multiple instances of -e.",
    )
    # logging
    parser.add_argument(
        "-o",
        "--output-file",
        help="""Log all messages to logfile.  The messages are normally reported to
               standard error.""",
    )
    parser.add_argument(
        "-a",
        "--append-output",
        help="""Append to logfile.  This is the same as  -o,  only  it  appends  to
               logfile  instead  of overwriting the old log file.  If logfile does
               not exist, a new file is created.
""",
    )
    parser.add_argument(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        help="""           Turn on debug output, meaning various information important to  the
    developers  of  Wget  if  it  does  not work properly.  Your system
    administrator  may  have  chosen  to  compile  Wget  without  debug
    support,  in  which  case  -d  will  not  work.   Please  note that
    compiling with debug support is always  safe---Wget  compiled  with
    the  debug  support  will not print any debug info unless requested
    with -d.
""",
    )
    parser.add_argument(
        "-q",
        "--queit",
        help="""Turn off Wget's output.
""",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="""           Turn on verbose output, with all the available data.   The  default
    output is verbose.
""",
        dest="verbose",
        action="store_true",
    )
    parser.add_argument(
        "-nv",
        "--no-verbose",
        dest="verbose",
        action="store_false",
        help="""         Turn  off verbose without being completely quiet (use -q for that),
      which means that error messages and  basic  information  still  get
      printed.
""",
    )

    parser.add_argument(
        "--report-speed", choices=["bits"], help="Output bandwidth as type.  The only accepted value is bits."
    )
    parser.add_argument("-i", "--input-file", dest="input_file")
    parser.add_argument("--input-metalink")
    parser.add_argument("--keep-badhash")
    parser.add_argument("--metalink-over-http")
    parser.add_argument("--preferred-location")
    parser.add_argument("--xattr")
    parser.add_argument("-F", "--forece-html")
    parser.add_argument("-B", "-base")
    parser.add_argument("--config")
    parser.add_argument("--rejected-log")

    # Download Options
    parser.add_argument("--bind-address")
    parser.add_argument("--bind-dns-address")
    parser.add_argument("--dns-servers")
    parser.add_argument("-t", "--tries")
    parser.add_argument("-O", "--output-document")

    parser.add_argument("-nc", "--no-clobber")
    parser.add_argument("--backups", type=int)
    parser.add_argument("--no-netrc")
    parser.add_argument("-c", "--continue")
    parser.add_argument("--start-pos")
    parser.add_argument("--progress", choices=["dot", "bar"], default="bar")
    parser.add_argument("--show-progess")
    parser.add_argument("-N", "--timestamping")
    parser.add_argument("--no-if-modified-since")
    parser.add_argument("--no-use-server-timestamps")
    parser.add_argument("-S", "--server-response")
    parser.add_argument("--spider")
    parser.add_argument("-T", "--timeout")
    parser.add_argument("--dns-timeout")
    parser.add_argument("--connect-timeout")
    parser.add_argument("--read-timeout")
    parser.add_argument("--limit-rate")
    parser.add_argument("--spider")
    parser.add_argument("-w", "--wait", type=float, dest="wait_times")
    parser.add_argument("--waitretry")
    parser.add_argument("--random-wait", action=BooleanOptionalAction, default=False)
    parser.add_argument("--no-proxy")
    parser.add_argument("-Q", "--quota")
    parser.add_argument("--no-dns-cache")
    parser.add_argument(
        "--restrict-file-names", choices=["unix", "windows", "nocontrol", "ascii", "lowercase", "uppercase"]
    )
    parser.add_argument("-6","--init6-only")
    parser.add_argument("-4","--init4-only")
    parser.add_argument("--prefer-family")
    parser.add_argument("--retry-connrefused")

    parser.add_argument("--user")
    parser.add_argument("--password")
    parser.add_argument("--ask-password")
    parser.add_argument("--no-iri")
    parser.add_argument("--local-encoding")
    parser.add_argument("--remote-encoding")
    parser.add_argument("--unlink")

    # Directory Options
    parser.add_argument("-nd","--no-directories")
    parser.add_argument("--ask-password")
    parser.add_argument("--ask-password")


    parser.add_argument("-P", "--directory-prefix", dest="directory_prefix")
    args = parser.parse_args()

    # print(options)
    print(args)
    filename = download_file(args.url, out=args.output)

    print()
    print("Saved under %s" % filename)


if __name__ == "__main__":
    main()

r"""
features that require more tuits for urlretrieve API
http://www.python.org/doc/2.6/library/urllib.html#urllib.urlretrieve

[x] autodetect filename from URL
[x] autodetect filename from headers - Content-Disposition
    http://greenbytes.de/tech/tc2231/
[ ] make HEAD request to detect temp filename from Content-Disposition
[ ] process HTTP status codes (i.e. 404 error)
    http://ftp.de.debian.org/debian/pool/iso-codes_3.24.2.orig.tar.bz2
[ ] catch KeyboardInterrupt
[ ] optionally preserve incomplete file
[ ] create temp file in current directory
[ ] resume download (broken connection)
[ ] resume download (incomplete file)
[ ] show progress indicator
    http://mail.python.org/pipermail/tutor/2005-May/038797.html
[x] do not overwrite downloaded file
 [x] rename file automatically if exists
[x] optionally specify path for downloaded file

[ ] options plan
 [x] -h, --help, --version (CHAOS speccy)
[ ] clpbar progress bar style
_ 30.0Mb at  3.0 Mbps  eta:   0:00:20   30% [=====         ]
[ ] test "bar \r" print with \r at the end of line on Windows
[ ] process Python 2.x urllib.ContentTooShortError exception gracefully
    (ideally retry and continue download)

    (tmpfile, headers) = urllib.urlretrieve(url, tmpfile, callback_progress)
  File "C:\Python27\lib\urllib.py", line 93, in urlretrieve
    return _urlopener.retrieve(url, filename, reporthook, data)
  File "C:\Python27\lib\urllib.py", line 283, in retrieve
    "of %i bytes" % (read, size), result)
urllib.ContentTooShortError: retrieval incomplete: got only 15239952 out of 24807571 bytes

[ ] find out if urlretrieve may return unicode headers
[ ] write files with unicode characters
    https://bitbucket.org/techtonik/python-wget/issues/7/filename-issue
  [ ] Python 2, Windows
  [ ] Python 3, Windows
  [x] Linux
[ ] add automatic tests
  [ ] specify unicode URL from command line
  [ ] specify unicode output file from command line
  [ ] test suite for unsafe filenames from url and from headers

[ ] security checks
  [ ] filename_from_url
  [ ] filename_from_headers
  [ ] MITM redirect from https URL
  [ ] https certificate check
  [ ] size+hash check helpers
    [ ] fail if size is known and mismatch
    [ ] fail if hash mismatch
"""
