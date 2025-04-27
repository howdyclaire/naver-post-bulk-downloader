import asyncio
import re
import aiohttp
from pathlib import Path
from sys import version_info
from urllib.parse import unquote, urlparse
from playwright.async_api import async_playwright

async def download_image(session, url, picture_path):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                picture_path.write_bytes(await response.read())
                print(f"[Download] Downloaded {picture_path.name}")
            else:
                print(f"[Download] Failed with status {response.status} for {url}")
    except Exception as e:
        print(f"[Download] Error downloading {url}: {e}")

async def download_images_from_collection(page, session, collection_url, post_title, folder_prefix, indexed):

    try:
        print(f"[Collection] Processing {collection_url}")

        safe_title = re.sub(r'[<>:"/\\|?*]', '_', post_title).strip()

        if indexed == "n":
            folder_name = f"{safe_title}"
        if indexed == "y":
            folder_name = f"{folder_prefix} - {safe_title}"

        desired_path = Path.cwd() / folder_name
        desired_path.mkdir(exist_ok=True)

        await page.goto(collection_url)
        await page.wait_for_timeout(3000)

        img_elements = await page.query_selector_all('img')

        if not img_elements:
            print(f"[Collection] No images found in {collection_url}")
            return

        print(f"[Collection] Found {len(img_elements)} images.")

        for img in img_elements:
            src = await img.get_attribute('src')
            if not src or 'post-phinf' not in src:
                continue

            picture_id = unquote(urlparse(src).path.split('/')[-1])
            picture_name = re.sub('[<>:"/\\|?*]', ' ', picture_id).strip()
            picture_path = desired_path / picture_name

            if picture_path.exists():
                print(f"[Collection] Skipping existing image: {picture_name}")
                continue

            await download_image(session, src, picture_path)
            await asyncio.sleep(0.5)

    except Exception as e:
        print(f"[Collection] Unexpected error in {collection_url}: {e}")

async def main_downloader(indexed, urls_filename="collection_urls.txt", titles_filename="post_titles.txt"):
    try:
        with open(urls_filename, 'r', encoding='utf-8') as f:
            collection_urls = [line.strip() for line in f if line.strip()]
        with open(titles_filename, 'r', encoding='utf-8') as f:
            post_titles = [line.strip() for line in f if line.strip()]
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    if len(collection_urls) != len(post_titles):
        print(f"Error: Number of URLs ({len(collection_urls)}) doesn't match number of titles ({len(post_titles)}).")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        async with aiohttp.ClientSession() as session:
            if indexed == "n":
                for collection_url, post_title in zip(collection_urls, post_titles):
                    await download_images_from_collection(page, session, collection_url, post_title, indexed)

            if indexed == "y":
                for index, (collection_url, post_title) in enumerate(zip(collection_urls, post_titles), start=1):
                    folder_prefix = f"{index:03}" 
                    await download_images_from_collection(page, session, collection_url, post_title, folder_prefix, indexed)


        await browser.close()


if __name__ == '__main__':
    assert version_info >= (3, 7), 'Script requires Python 3.7+.'
    indexed = input("Do you want folder names to be indexed (e.g., beginning with 001, 002, etc)? Y or N: ").lower()
    if indexed == "y" or indexed == "n":
        asyncio.run(main_downloader(indexed))
    else:
        print(f"Invalid value {indexed}. Exiting.")
