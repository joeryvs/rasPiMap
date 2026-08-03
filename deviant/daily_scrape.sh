#!/usr/bin/bash

set -eu

today=$(date +%Y-%j)

today_map=art-$today
today_index=front-page/index-$today.html
today_art_links="art-$today.txt"
echo $today
echo $today_map

echo $today_index

if [[ ! -n $VIRTUAL_ENV ]] ; then
    echo "not in a virtual env exiting"
    exit 1;
fi

if [ -d $today_map ] ; then
    echo "directory exist no longer. ending call"
    exit 1;
fi

mkdir -p $today_map
curl https://www.deviantart.com/ --output "$today_index" --silent
# call python script
python main.py json_art_pre -i "$today_index" -o "$today_art_links"
# sort and unique
sort "$today_art_links" --unique -o "$today_art_links"
# Download all images
wget --user-agent=Mozilla --wait=0.2 --random-wait --input-file="./art-$today.txt" --directory-prefix="$today_map" --no-verbose

pwd
# clean
../remove_post.sh $today_map
