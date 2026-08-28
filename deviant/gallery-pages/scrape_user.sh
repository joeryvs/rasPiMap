#!/usr/bin/bash

set -eu
# 2 or 3 arguments, arg 1 is the username, arg 2 is the amount of pages to scrape , if there are 3 argument assume 2 is the start end 3 is the end
if [[ $# -lt 2 || $# -gt 3 ]] ; then
    echo "$0 USER AMOUNT"
    echo "$0 USER START END"
    exit 1;
fi
if [[ $# == 2 ]] ; then
    user="$1"
    start="1"
    end="$2"
fi
if [[ $# == 3 ]] ; then
    user="$1"
    start="$2"
    end="$3"
fi

# check first argument in a valid user
re='^[a-z0-9\-]+$'
if ! [[ $user =~ $re ]] ; then
    echo "error: not a valid user" >&2;
    exit 1;
fi

# check second argument is a number
re='^[0-9]+$'
if ! [[ $start =~ $re ]] ; then
   echo "error: Not a number" >&2;
   exit 1
fi

if ! [[ $end =~ $re ]] ; then
   echo "error: Not a number" >&2;
   exit 1
fi

url="https://www.deviantart.com/$user/gallery?page=[$start-$end]"
dir="$(dirname $0)/$user"
# create directory
mkdir -p "$dir"
# download all pages
curl --limit-rate 8M "$url" --output "$dir/gallery_page_#1.html" --fail
