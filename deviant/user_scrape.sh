#!/usr/bin/bash

WAIT_TIME=0.7

if [[ ! -n $(echo "$VIRTUAL_ENV") ]] ; then
    echo "PROGRAM NOT IN VENV EXITING"
    exit 1
fi


# CHANGE constants on next run
ART_PAGE_URL="eravuru_pages.txt"
ART_PAGE_STORE_DIR="eravuru_art"

IMAGE_LOCATION="eravuru_images_full"
DESCRIPTION_LOCATION="eravuru_description"

# download each page using wget
# wget --input-file="$ART_PAGE_URL" --directory-prefix="$ART_PAGE_STORE_DIR" --random-wait --wait="$WAIT_TIME"

# find all img locations
# python webscrape_dev.py main_image -i "$ART_PAGE_STORE_DIR" -o "eravuru_main_image.txt"

# write description folder
# python webscrape_dev.py description -i "$ART_PAGE_STORE_DIR" -o "$DESCRIPTION_LOCATION"

# download images
wget --input-file="eravuru_main_image.txt" --directory-prefix="eravuru_main_image.txt" --random-wait --wait="$WAIT_TIME"

# rename file
../remove_post.sh "$IMAGE_LOCATION"
