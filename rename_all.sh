#!/usr/bin/bash

show_help() {
    cat << EOF
    USAGE: ${0##/} [--verbose] [--interactive] (dir)+
    Renames all files in the directory
EOF
}

echo "total number of arguments are: $#"
echo "$0 $@"

POSITIONAL_ARG=()

while [[ $# -gt 0 ]];do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;

        *)
            POSITIONAL_ARG+=("$1")
            shift
            ;;
    esac
done

rename_file_to_extension() {
    OLD_NAME="$1"
    TYPE=$( file "$OLD_NAME" -b -0 --mime-type)
    HASH_FILENAME="$(sha256sum "$OLD_NAME")"
    # it works dont know why
    HASH_FILENAME=($HASH_FILENAME)
    HASH=${HASH_FILENAME[0]}
    PARENT_DIR="$(dirname "$OLD_NAME")"
    NEW_NAME=""
    case $TYPE in
        image/webp)
            NEW_NAME="$PARENT_DIR/$HASH.webp"
            ;;
        image/jpeg)
            NEW_NAME="$PARENT_DIR/$HASH.jpeg"
            ;;
        image/png)
            NEW_NAME="$PARENT_DIR/$HASH.png"
            ;;
        image/svg)
            NEW_NAME="$PARENT_DIR/$HASH.svg"
            ;;
        image/jpg)
            NEW_NAME="$PARENT_DIR/$HASH.jpg"
            ;;
        image/gif)
            NEW_NAME="$PARENT_DIR/$HASH.gif"
            ;;
        image/svg+xml)
            NEW_NAME="$PARENT_DIR/$HASH.svg"
            ;;
        apllication/javascript)
            NEW_NAME="$PARENT_DIR/$HASH.js"
            ;;
        text/plain)
            NEW_NAME="$PARENT_DIR/$HASH.txt"
            ;;
        text/html)
            NEW_NAME="$PARENT_DIR/$HASH.html"
            ;;
    esac

    if [ ! -z $NEW_NAME ]; then
        mv --verbose "$OLD_NAME" "$NEW_NAME"
    else
        echo "didnt rename '$OLD_NAME', because '$TYPE' is not accounted for"
    fi
}

# verify all positinal arguments point to a directory
for dir in ${POSITIONAL_ARG[*]}; do
    echo "$dir"
    if [ ! -d "$dir" ]; then
        echo "$dir is not a directory"
        exit 1
    fi
done;

# rename all files into their sha256
for dir in ${POSITIONAL_ARG[*]}; do
    find "$dir" -maxdepth 1 -type f  | while read -r file; do rename_file_to_extension "$file"; done
done
