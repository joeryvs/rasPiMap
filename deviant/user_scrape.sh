#!/usr/bin/bash

WAIT_TIME=0.7

if [[ ! -n $(echo "$VIRTUAL_ENV") ]] ; then
    echo "PROGRAM NOT IN VENV EXITING"
    exit 1
fi


# CHANGE constants on next run
user="eravuru"
ART_PAGE_URL=""$user"_pages.txt"
ART_PAGE_STORE_DIR=""$user"_art"

IMAGE_URLS_FILE=""$user"_main_image.txt"
IMAGE_LOCATION=""$user"_main_images"
DESCRIPTION_LOCATION=""$user"_description"


# download each page using wget
wget --input-file="$ART_PAGE_URL" --directory-prefix="$ART_PAGE_STORE_DIR" --random-wait --wait="$WAIT_TIME"
# find all img locations
python webscrape_dev.py main_image -i "$ART_PAGE_STORE_DIR" -o "$IMAGE_URLS_FILE"
# write description folder
python webscrape_dev.py description -i "$ART_PAGE_STORE_DIR" -o "$DESCRIPTION_LOCATION"
# download images
wget --input-file="$IMAGE_URLS_FILE" --directory-prefix="$IMAGE_LOCATION" --random-wait --wait="$WAIT_TIME"
# rename file
../remove_post.sh "$IMAGE_LOCATION"
