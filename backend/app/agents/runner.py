import socket
old_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args, **kwargs):
    responses = old_getaddrinfo(*args, **kwargs)
    return [response for response in responses if response[0] == socket.AF_INET]
socket.getaddrinfo = new_getaddrinfo

import asyncio
import schedule
import time
import logging
from .scraper import run_scraping_agent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent.log')  # Log to file for debugging
    ]
)
logger = logging.getLogger(__name__)

async def run_agent():
    """Run the real content scraping agent once"""
    try:
        logger.info("Starting REAL content scraping agent...")
        stored_count = await run_scraping_agent()
        
        if stored_count > 0:
            logger.info(f"Real content scraping completed - stored {stored_count} new articles")
        else:
            logger.info("No new articles stored - may already exist in database")
            
        return stored_count
        
    except Exception as e:
        logger.error(f"Error in real scraping agent: {e}")
        return 0

def scheduled_job():
    """Wrapper for scheduled jobs"""
    return asyncio.create_task(run_agent())

def start_scheduler():
    """Start the scheduled agent for real content"""
    # Run immediately on startup
    asyncio.create_task(run_agent())
    
    # Schedule regular runs
    schedule.every(30).minutes.do(scheduled_job)  # Quick updates
    schedule.every(6).hours.do(scheduled_job)     # Deep scrape
    
    logger.info("Real content agent scheduler started")
    logger.info("   - Running every 30 minutes for quick updates")
    logger.info("   - Deep scrape every 6 hours")

async def run_scheduler():
    """Run the scheduler in background"""
    while True:
        schedule.run_pending()
        await asyncio.sleep(60)  # Check every minute