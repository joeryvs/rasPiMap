#!/usr/bin/bash

WAIT_TIME=11

if [[ ! -n $(echo "$VIRTUAL_ENV") ]] ; then
    echo "PROGRAM NOT IN VENV EXITING"
    exit 1
fi

if [[ $# == 0 ]] ; then
    echo "GIVE 1 argument"
    exit 1;
fi
POSITIONAL_ARGS=()
while [[ $# != 0 ]] ; do
    input="$1"
    re='^[a-z0-9\-]+$'
    if ! [[ $input =~ $re ]] ; then
        echo "INVALID USER $input";
        exit 1;
    fi
    POSITIONAL_ARGS+=("$input")
    shift

done;


for user in "${POSITIONAL_ARGS[@]}" ; do
    echo $user
    USER_URL="https://www.deviantart.com/"$user"/gallery?page=1"
    USER_OUTPUT=""$user"_gal_page_1.html"

    curl -s "$USER_URL" -o "$USER_OUTPUT"
    sleep "$WAIT_TIME"
done;
exit 0;
