import requests
from bs4 import BeautifulSoup
import os
import time

LINKEDIN_URL = os.environ["LINKEDIN_URL"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

SEEN_FILE = "seen_jobs.txt"


def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        for job in seen:
            f.write(job + "\n")


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload)


def scrape():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }

    resp = requests.get(LINKEDIN_URL, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")

    seen = load_seen()
    new_seen = set(seen)

    # LinkedIn job cards
    jobs = soup.select(".base-card")

    for job in jobs:
        title = job.select_one(".base-search-card__title")
        company = job.select_one(".base-search-card__subtitle")
        posted = job.select_one("time")
        link = job.select_one("a.base-card__full-link")

        if not (title and company and posted and link):
            continue

        job_url = link["href"].split("?")[0].strip()

        # avoid duplicates
        if job_url in seen:
            continue

        # Build Telegram message
        msg = (
            f"🔥 <b>New Job Posted</b>\n\n"
            f"👔 <b>{title.text.strip()}</b>\n"
            f"🏢 {company.text.strip()}\n"
            f"⏰ {posted.text.strip()}\n"
            f"🔗 {job_url}"
        )

        send_telegram(msg)
        new_seen.add(job_url)

    save_seen(new_seen)


if __name__ == "__main__":
    scrape()
