#!/usr/bin/bash

if [[ $# != 1 ]] ; then
    echo "usage: $0 NAME"
    exit 1;
fi

name="$1"

gallary_base_url="https://www.deviantart.com/$name/gallery?page=1"
current_dir="$(dirname $0)"
main_gallery_page="$current_dir/"$name"_gal_page_1.html"
curl "$gallary_base_url" -o "$main_gallery_page"

echo $gallary_base_url $current_dir $main_gallery_page
# find the highest available gallary page
gallary_amount=$(python "$current_dir/webscrape_dev.py" highest_user_page_number -o - -i "$main_gallery_page" --quiet --log-level CRITICAL)
# download all gallary pages, extracted into seperate sh script in gallary-pages
"$current_dir/gallary-pages/scrape_user.sh" "$name" "$gallary_amount"

# extract individual pages into a single file
python "$current_dir/webscrape_dev.py" art -i "$current_dir/gallary-pages/$name" -o "$current_dir/"$name"_art.txt" --sort --uni

sleep 100

# download each individual page
art_pages_dir="$current_dir/Art-Pages/"$name"_art"
wget --no-verbose --input-file="$current_dir/"$name"_art.txt" --directory-prefix="$art_pages_dir" --wait 8.0 --random-wait

sleep 3

python "$current_dir/webscrape_dev.py" description -i "$art_pages_dir" -o "$current_dir/"$name"_desc"
python "$current_dir/webscrape_dev.py" story -i "$art_pages_dir" -o "$current_dir/"$name"_story"
art_link_file="$current_dir/"$name"_main_images.txt"
python "$current_dir/webscrape_dev.py" main_image -i "$art_pages_dir" -o "$art_link_file"

sleep 7
image_output_dir="$current_dir/"$name"_images"
wget --no-verbose --input-file="$art_link_file" --directory-prefix="$image_output_dir" --wait 5.3 --random-wait

# remove the query parameters
"$current_dir/../remove_post.sh" "$image_output_dir"
