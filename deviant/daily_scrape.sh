#!/usr/bin/bash

set -eu

today=$(date +%Y-%j)

today_map=art-$today
today_index=index-$today.html
echo $today
echo $today_map
echo $today_index

if [[ -n $VIRTUAL_ENV ]] ; then
    echo "not in a virtual env exiting"
    exit 1;
fi

if [ -d $today_map ] ; then
    echo "directory exist no longer. ending call"
    exit 1;
fi

mkdir -p $today_map
curl https://www.deviantart.com/ -o "$today_index"
# call python script
python webscrape_dev.py images -i "$today_index" -o "art-$today.txt"
# Download all images
wget --user-agent=Mozilla --wait=0.2 --random-wait --input-file="./art-$today.txt" --directory-prefix="$today_map"

pwd
# clean
../remove_post.sh $today_map
