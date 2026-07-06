#!/usr/bin/bash

set -eu

if [[ $# != 1 ]]; then
    echo "Provide only 1 argument"
    exit 1;
fi

tag="$1"
today=$(date +%Y-%j)

url="https://www.deviantart.com/tag/$tag"

today_tag_map="tag/art-$tag-$today"
today_tag_index="tag/front-page/index-$tag-$today.html"
today_tag_art_links="tag/links/art-$today.txt"


if [[ ! -n $VIRTUAL_ENV ]] ; then
    echo "not in a virtual env exiting"
    exit 1;
fi

# create maps
mkdir -p tag/{front-page,links}

if [ -e $today_tag_index ] ; then
    echo "Tag is already downloaded. ending call"
    exit 1;
fi

mkdir -p "$today_tag_map"
curl "$url" -o "$today_tag_index"
# call python script
python webscrape_dev.py no_crop_large -i "$today_tag_index" -o "$today_tag_art_links"
# sort and unique
sort "$today_tag_art_links" --unique -o "$today_tag_art_links"
# Download all images
wget --wait=0.2 --random-wait --input-file="$today_tag_art_links" --directory-prefix="$today_tag_map" --quiet

pwd
# clean
../remove_post.sh "$today_tag_map"
