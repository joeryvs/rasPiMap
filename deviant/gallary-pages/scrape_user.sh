#!/usr/bin/bash

# 2 arguments, arg 1 is the username, arg 2 is the amount of pages to scrape
if [[ $# != 2 ]] ; then
    echo "$0 USER AMOUNT"
    exit 1;
fi
user="$1"
amount="$2"

# check first argument in a valid user
re='^[a-z0-9\-]+$'
if ! [[ $user =~ $re ]] ; then
    echo "error: not a valid user" >&2;
    exit 1;
fi

# check second argument is a number
re='^[0-9]+$'
if ! [[ $amount =~ $re ]] ; then
   echo "error: Not a number" >&2;
   exit 1
fi

url="https://www.deviantart.com/$user/gallery?page=[1-$amount]"
dir="$(dirname $0)/$user"
# create directory
mkdir -p "$dir"
# download all pages
curl --limit-rate 1000M "$url" --output "$dir/gallery_page_#1.html" --fail
