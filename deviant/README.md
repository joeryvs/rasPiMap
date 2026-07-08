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

## Taking from source

when downloading an individual page, of front-page image or other. you usually get a bunch of JS

find the script with the id of *_R_*, that sets SEVERAL fields on window, the most important ones are 
*__INITIAL_I18N__* which deals with translation and *__INITIAL_STATE__* which deals with all the state required 
for efficient use of a progressive web-app.

in the *__INITIAL_STATE__* variable taks *@@entities* en then *deviantion* and you get a JS object for which the keys are string-numbers and the values 
are objects with several fields.  The most important one is *media*, 
which contains the fields *baseUri*, *prettyName*, *token* and *types*

*baseUri* and *prettyName* are both strings, *token* is a list of strings.  
*types* is an array of objects where each object has a *t*, *r*, *c*, *h*, *w* field with an optional *ss* field which is an array of objects.  
one of the *types* should have {'t':'fullview'} and that item can be used to construct the full image url.

with the rough formula

```js
const url = baseUri + (types.find(x => x.t == "fullview")?.c ?? "").replace("<prettyName>",prettyName) + "?token=" + token[0]
```
