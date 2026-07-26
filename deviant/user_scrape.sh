#!/usr/bin/bash

WAIT_TIME=11

if [[ ! -n $(echo "$VIRTUAL_ENV") ]] ; then
    echo "PROGRAM NOT IN VENV EXITING"
    exit 1
fi

if [[ $# != 1 ]] ; then
    echo "GIVE 1 argument"
    exit 1;
fi

# CHANGE constants on next run
user="$1"
ART_PAGE_URL=""$user"_pages.txt"

if [[ ! -r $ART_PAGE_URL ]]; then
    echo "$ART_PAGE_URL does not exist or no read access"
    exit 1
fi
ART_PAGE_STORE_DIR="Art-Pages/"$user"_art"


IMAGE_URLS_FILE=""$user"_main_image.txt"
IMAGE_LOCATION=""$user"_main_images"
DESCRIPTION_LOCATION=""$user"_description"


# download each page using wget
wget --input-file="$ART_PAGE_URL" --directory-prefix="$ART_PAGE_STORE_DIR" --random-wait --wait="$WAIT_TIME" --no-verbose
# find all img locations
python webscrape_dev.py main_image -i "$ART_PAGE_STORE_DIR" -o "$IMAGE_URLS_FILE"
# write description folder
python webscrape_dev.py description -i "$ART_PAGE_STORE_DIR" -o "$DESCRIPTION_LOCATION"
# download images
wget --input-file="$IMAGE_URLS_FILE" --directory-prefix="$IMAGE_LOCATION" --random-wait --wait="$WAIT_TIME"
# rename file
../remove_post.sh "$IMAGE_LOCATION"
