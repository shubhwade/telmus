import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # INFY Browser View
        await page.goto('file:///C:/Users/Shubh/OneDrive/Documents/Desktop/telmus/INFY_dashboard.html')
        await page.screenshot(path='C:/Users/Shubh/.gemini/antigravity-ide/brain/a2c58e98-3b25-4339-9477-a2c35c558eab/infy_browser.png', full_page=True)
        
        # INFY Print View
        await page.emulate_media(media='print')
        await page.screenshot(path='C:/Users/Shubh/.gemini/antigravity-ide/brain/a2c58e98-3b25-4339-9477-a2c35c558eab/infy_print.png', full_page=True)
        
        # Compare Print View
        await page.goto('file:///C:/Users/Shubh/OneDrive/Documents/Desktop/telmus/INFYvsTCS_dashboard.html')
        await page.emulate_media(media='print')
        await page.screenshot(path='C:/Users/Shubh/.gemini/antigravity-ide/brain/a2c58e98-3b25-4339-9477-a2c35c558eab/compare_print.png', full_page=True)
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
