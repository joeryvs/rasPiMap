#!/usr/bin/bash

show_help() {
    cat << EOF
    USAGE: ${0##/} (dir)+
    Removes everything after the ? in the file name
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

rename_file() {
    OLD_NAME="$1"
    parent_dir="$(dirname "$OLD_NAME")"
    file_name="$(basename "$OLD_NAME")"
    IFS='?' read -ra ARR  <<< $file_name
    new_name=${ARR[0]}
    NEW_NAME="$parent_dir/$new_name"
    echo $NEW_NAME
    mv --verbose --interactive "$OLD_NAME" "$NEW_NAME"
}

# verify all positinal arguments point to a directory
for dir in ${POSITIONAL_ARG[*]}; do
    echo "$dir"
    if [ ! -d "$dir" ]; then
        echo "$dir is not a directory"
        exit 1
    fi
done;

# rename all files
for dir in ${POSITIONAL_ARG[*]}; do
    find "$dir" -maxdepth 1 -type f  | while read -r file; do rename_file "$file"; done
done
