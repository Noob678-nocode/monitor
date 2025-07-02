import asyncio
from playwright.async_api import async_playwright
import requests
import os

ZEALY_URL = "https://zealy.io/cw/invogamingalliance/questboard/sprints"
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

last_count = 0

async def check_zealy():
    global last_count
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(ZEALY_URL)
        await page.wait_for_timeout(5000)  # wait 5 seconds for content

        quests = await page.query_selector_all("div.quest-card")
        count = len(quests)

        if count != last_count and last_count != 0:
            message = f"⚡ Zealy Update!\nTasks changed: {last_count} → {count}"
            send_telegram(message)

        print(f"✅ Checked: {count} quests found")
        last_count = count
        await browser.close()

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, json=data)

async def main():
    while True:
        await check_zealy()
        await asyncio.sleep(60)  # ⏱ Check every 60 seconds

asyncio.run(main())
