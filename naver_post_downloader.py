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

async def download_images_from_collection(page, session, collection_url):
    try:
        print(f"[Collection] Processing {collection_url}")
        title_match = re.search(r'volumeNo=(\d+)', collection_url)
        if not title_match:
            print(f"[Collection] Could not extract volumeNo from URL: {collection_url}")
            return

        title = title_match.group(1)
        desired_path = Path.cwd() / title
        desired_path.mkdir(exist_ok=True)

        await page.goto(collection_url)
        await page.wait_for_timeout(3000)  # Wait for JavaScript to load

        img_elements = await page.query_selector_all('img')

        if not img_elements:
            print(f"[Collection] No images found in {collection_url}")
            return

        print(f"[Collection] Found {len(img_elements)} images.")

        for img in img_elements:
            src = await img.get_attribute('src')
            if not src or 'post-phinf' not in src:
                continue  # Only download actual post images

            picture_id = unquote(urlparse(src).path.split('/')[-1])
            picture_name = re.sub('[<>:\"/|?*]', ' ', picture_id).strip()
            picture_path = desired_path / picture_name

            if picture_path.exists():
                print(f"[Collection] Skipping existing image: {picture_name}")
                continue

            await download_image(session, src, picture_path)
            await asyncio.sleep(0.5)  # Tiny pause between downloads

    except Exception as e:
        print(f"[Collection] Unexpected error in {collection_url}: {e}")

async def main_downloader(input_filename="collection_urls.txt"):
    try:
        with open(input_filename, 'r') as f:
            collection_urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: The file {input_filename} was not found.")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        async with aiohttp.ClientSession() as session:
            for collection_url in collection_urls:
                await download_images_from_collection(page, session, collection_url)

        await browser.close()

if __name__ == '__main__':
    assert version_info >= (3, 7), 'Script requires Python 3.7+.'
    asyncio.run(main_downloader())
