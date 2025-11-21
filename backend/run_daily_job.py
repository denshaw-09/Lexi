import asyncio
import time
# Change the import to use the function we created in scraper.py
from app.agents.scraper import run_scraping_agent
from app.agents.reporter import send_daily_briefing

async def main():
    start_time = time.time()
    print("\n Lexi Agent: Waking up...")

    # 1. Run the Agent (Scrape -> AI -> DB)
    print("\n PHASE 1: Gathering Intelligence...")
    # This function now handles everything (fetching + AI analysis + saving)
    count = await run_scraping_agent() 
    
    # 2. Run Reporter (Email)
    if count > 0:
        print("\n PHASE 2: Reporting...")
        send_daily_briefing()
    else:
        print("\n No new articles to report.")

    duration = round(time.time() - start_time, 2)
    print(f"\n Mission Complete in {duration} seconds. Going to sleep.")

if __name__ == "__main__":
    # Fix for Windows Event Loop
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())