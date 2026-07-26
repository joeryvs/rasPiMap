#!/usr/bin/bash

set -eu



if [[ ! -n $VIRTUAL_ENV ]] ; then
    echo "not in a virtual env exiting"
    exit 1;
fi

if [[ $# == 0 ]]; then
    echo "Provide arguments"
    exit 1;
fi

today=$(date +%Y-%j)

ALL_TAGS=()
while [[ $# != 0 ]]; do
    ALL_TAGS+=("$1")
    shift
done;

# create maps
mkdir -p tag/{front-page,links}

# exaust all parameters
for tag in "${ALL_TAGS[@]}"; do
    echo $tag

    url="https://www.deviantart.com/tag/$tag"

    today_tag_map="tag/art-$tag-$today"
    today_tag_index="tag/front-page/index-$tag-$today.html"
    today_tag_art_links="tag/links/art-$tag-$today.txt"

    echo $url $today_tag_map $today_tag_index $today_tag_art_links




    if [ -e $today_tag_index ] ; then
        echo "Tag $tag is already downloaded."
        continue
    fi


    mkdir -p "$today_tag_map"
    curl "$url" --output "$today_tag_index" --silent
    # call python script
    python main.py no_crop_large -i "$today_tag_index" -o "$today_tag_art_links" --no-sort --no-unique
    # sort and unique
    sort "$today_tag_art_links" --unique -o "$today_tag_art_links"
    # Download all images
    wget --input-file="$today_tag_art_links" --directory-prefix="$today_tag_map" --quiet

    pwd
    # clean
    ../remove_post.sh "$today_tag_map"
    sleep 3

done;
exit 0
