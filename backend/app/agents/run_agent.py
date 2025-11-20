import asyncio
import schedule
import time
from app.agents.scraper import run_scraping_agent

async def main():
    await run_scraping_agent()

def job():
    asyncio.run(main())

# Schedule to run every 30 minutes
schedule.every(30).minutes.do(job)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)