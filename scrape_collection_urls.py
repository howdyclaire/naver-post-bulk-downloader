import asyncio
from playwright.async_api import async_playwright, TimeoutError

async def scrape_all_post_urls(main_url, output_filename="collection_urls.txt"):
    post_urls = set()

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

        await browser.close()

    with open(output_filename, 'w') as f:
        for url in sorted(post_urls):
            f.write(url + '\n')
    print(f"\n✅ Found {len(post_urls)} post URLs and saved them to {output_filename}")

if __name__ == '__main__':
    homepage_url = input("Enter the Naver Post homepage URL (e.g., https://m.post.naver.com/my.naver?memberNo=37024524): ").strip()
    if homepage_url:
        asyncio.run(scrape_all_post_urls(homepage_url))
    else:
        print("No URL entered. Exiting.")
