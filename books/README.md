# How to extract images

download pages.
use the correct path

```sh
curl https://www.deviantart.com -o index.html
```

extract all page links with webscrape_dev.py

```sh
python webscrape_dev.py pages -i index.html -o art_links.txt
```

The links get saved in art_links.txt

inside a new directory run `wget --content-disposittion -i ../art_links.txt` to retrieve more pages.

Use the following options `--user-agent=Mozilla --random-wait`

## Rename
in the root of the directory is a file for which to rename all images to their hash
## Youtube

perform a POST request to **https://youtube.com/youtubei/v1/browse?prettyPrint=false**
with some encrypted POST data. you will recieve some **applition/json;charset=UTF-8**  
To find the urls go to **onResponseReceivedEndpoints.onclickingParams[0].appendContinuationItemsActions.continuationItems** this is a JS array.  
in each item find **backstagePostThreadRenderer.post.backstagePostRenderer.backstageAttachement.backstageImageRenderer.image.thumbnails** this is a JS array of objects
for each use **url** to get the full url which links to **yt3.ggpht.com**

THe post Data consist of *body*

need more debug info
