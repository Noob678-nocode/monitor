import os
import asyncio
from playwright.async_api import async_playwright
import requests

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
URL = os.environ["TARGET_URL"]

previous_tasks = set()

async def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Failed to send Telegram message:", e)

async def main():
    print("✅ Bot started. Monitoring Zealy...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        while True:
            try:
                await page.goto(URL, timeout=60000)
                await page.wait_for_selector('[data-testid="quest-title"]', timeout=10000)

                task_elements = await page.query_selector_all('[data-testid="quest-title"]')
                task_titles = set([await el.inner_text() for el in task_elements])

                if not previous_tasks:
                    previous_tasks.update(task_titles)
                    print("Initial task list loaded.")
                elif task_titles != previous_tasks:
                    new_tasks = task_titles - previous_tasks
                    if new_tasks:
                        message = "🆕 New Zealy task(s) detected:\n" + "\n".join(f"• {t}" for t in new_tasks)
                        await send_telegram_message(message)
                        print("Sent Telegram notification.")
                    previous_tasks = task_titles
                else:
                    print("No new tasks found.")

            except Exception as e:
                print("Error while checking tasks:", e)

            await asyncio.sleep(60)  # Check every 60 seconds

if __name__ == "__main__":
    asyncio.run(main())
