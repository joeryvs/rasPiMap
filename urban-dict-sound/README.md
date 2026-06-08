# Urban Dictionary webscraping

**step 1**
download everything from the pages. use curl
first use binary search to find the last page.  
base url: **https://www.urbandictionary.com/?page={n}** up to 143
```sh
curl https://www.urbandictionary.com/?page=[0-143] -o page_#1.html
```

use the python file to extract the sound links.
```
python extract_sound_files.py
```

Use wget to download the sound, and fix remove the end output
```sh
wget -i ../urban_dictionary_sounds.txt
```

To remove the arguments after the ? use the following command
```sh
find ./ -type f | while read file_name; do \
base=$(basename $file_name)
d=$(dirname $file_name)
IFS='?' read -a parts <<< $file_name
mv -vi "$file_name" "$d/${parts[0]}"
done;
```

or use this command from [StackOverflow](https://stackoverflow.com/questions/26736156/using-wget-but-ignore-url-parameters) 
```sh
rename -v -n 's/[?].*//' *[?]*
```