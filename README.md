# naver-post-bulk-downloader
Python3 script to bulk download all images from all posts on a user's Naver Post page (https://m.post.naver.com/my.naver?memberNo=XXXXXXXX)

## Requirements
- Python 3.7+
- aiohttp
- playwright
- beautifulsoup4

## How to use
- Run `scrape_collection_urls.py` and enter a valid Naver Post URL (example: https://m.post.naver.com/my.naver?memberNo=37024524)
- Ensure `collection_urls.txt` and `post_titles.txt` files exists in the same folder as `naver_post_downloader.py`
- Run `naver_post_downloader.py`

## Notes
This tool is inspired by and based on the [naver_post_downloader](https://github.com/nylonicious/naver-post-downloader) by [nylonicious](https://github.com/nylonicious)
