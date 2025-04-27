import asyncio
import re
from playwright.async_api import async_playwright, TimeoutError

async def scrape_all_post_urls(main_url, collection_filename="collection_urls.txt", title_filename="post_titles.txt"):
    post_urls = set()
    post_titles = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(main_url)
        await page.wait_for_selector('a.link_end')

        # Keep clicking the '더보기' (Load more) button until it disappears or times out
        while True:
            try:
                await page.click('button.btn_lst_more', timeout=3000)
                await page.wait_for_timeout(1000)  # Small delay for content to load
            except TimeoutError:
                print("No more 'Load more' button or timeout reached.")
                break

        # After loading all posts, grab all the links
        links = await page.query_selector_all('a.link_end')
        for link in links:
            href = await link.get_attribute('href')
            if href and href.startswith('/viewer/postView.naver?'):
                full_url = "https://m.post.naver.com" + href
                post_urls.add(full_url)
                print(full_url)

        # Grab all of the post titles
        titles = await page.query_selector_all('strong.tit_feed')
        for title in titles:
            strong = await title.text_content()
            if strong:
                cleaned_title = re.sub(r'[<>:"/\\|?*]', '_', strong).strip()
                post_titles.add(cleaned_title)
                print(f'Extracted and cleaned title: {cleaned_title}')

        await browser.close()

    with open(collection_filename, 'w') as f:
        for url in sorted(post_urls):
            f.write(url + '\n')
    print(f"\n✅ Found {len(post_urls)} post URLs and saved them to {collection_filename}")

    with open(title_filename, 'w', encoding='utf-8') as g:
        for title in sorted(post_titles):
            g.write(title + '\n')
    print(f"\n✅ Found {len(post_titles)} post titles and saved them to {title_filename}")

if __name__ == '__main__':
    homepage_url = input("Enter the Naver Post homepage URL (e.g., https://m.post.naver.com/my.naver?memberNo=37024524): ").strip()
    title_match = re.search(r'https://m\.post\.naver\.com/my\.naver\?memberNo=(\d+).*', homepage_url)
    if title_match:
        asyncio.run(scrape_all_post_urls(homepage_url))
    else:
        print("Invalid URL entered. Exiting.")
