import aiohttp
import asyncio
import feedparser
import socket
import logging
import time
import dateutil.parser
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from app.core.config import settings
from .language_detector import LanguageFilter
from supabase import create_client 
from .processor import analyze_content

logger = logging.getLogger(__name__)

class Web3ContentScraper:
    def __init__(self):
        self.session = None
        self.language_filter = LanguageFilter()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(family=socket.AF_INET, ssl=False)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=30),
            headers=self.headers
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _extract_text_from_entry(self, entry) -> str:
        content = ""
        if hasattr(entry, 'content'):
            content = entry.content[0].value
        elif hasattr(entry, 'summary'):
            content = entry.summary
        elif hasattr(entry, 'description'):
            content = entry.description
        
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            return soup.get_text()
        return ""

    def _parse_date(self, entry) -> str:
        """Extract and parse date from feed entry safely"""
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                return datetime.fromtimestamp(time.mktime(entry.published_parsed)).isoformat()
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                return datetime.fromtimestamp(time.mktime(entry.updated_parsed)).isoformat()
            elif hasattr(entry, 'published'):
                return dateutil.parser.parse(entry.published).isoformat()
            elif hasattr(entry, 'updated'):
                return dateutil.parser.parse(entry.updated).isoformat()
        except Exception:
            pass
        return datetime.now().isoformat()

    def clean_article_content(self, title: str, summary: str) -> tuple[str, str]:
        clean_title = self.language_filter.clean_text(title)
        clean_summary = self.language_filter.clean_text(summary)
        
        if len(clean_title) > 200:
            clean_title = clean_title[:197] + "..."
        if len(clean_summary) > 3000:
            clean_summary = clean_summary[:2997] + "..."
            
        return clean_title, clean_summary
    
    # --- GENERIC FEED SCRAPER ---
    async def scrape_feed(self, feed_url: str, source: str, default_tag: str, limit: int = 10) -> List[Dict]:
        articles = []
        try:
            async with self.session.get(feed_url) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = feedparser.parse(content)
                    
                    for entry in feed.entries[:limit]:
                        title = entry.title
                        raw_text = self._extract_text_from_entry(entry)
                        
                        if not self.language_filter.should_include_article(title, raw_text):
                            continue
                        
                        clean_title, clean_summary = self.clean_article_content(title, raw_text)
                        
                        # EXTRACT DATE HERE while we have the 'entry' object
                        pub_date = self._parse_date(entry)

                        article = {
                            "title": clean_title,
                            "url": entry.link,
                            "summary": clean_summary,
                            "source": source,
                            "ecosystem_tag": default_tag,
                            "published_at": pub_date  # Store it now
                        }
                        articles.append(article)
        except Exception as e:
            logger.error(f"Error scraping {feed_url}: {e}")
        return articles

    # --- SPECIFIC IMPLEMENTATIONS ---
    async def scrape_ethereum_blog(self) -> List[Dict]:
        logger.info("Scraping Ethereum ecosystem...")
        tasks = [
            self.scrape_feed("https://blog.ethereum.org/feed.xml", "ethereum", "ethereum"),
            self.scrape_feed("https://newsletter.banklesshq.com/feed", "bankless", "ethereum")
        ]
        results = await asyncio.gather(*tasks)
        return [item for sublist in results for item in sublist]

    async def scrape_farcaster(self) -> List[Dict]:
        logger.info("Scraping Farcaster blogs...")
        tasks = [
            self.scrape_feed("https://farcaster.mirror.xyz/feed/atom", "farcaster", "farcaster"),
            self.scrape_feed("https://purple.mirror.xyz/feed/atom", "farcaster", "farcaster")
        ]
        results = await asyncio.gather(*tasks)
        return [item for sublist in results for item in sublist]

    async def scrape_solana_ecosystem(self) -> List[Dict]:
        logger.info("Scraping Solana ecosystem...")
        tasks = [
            self.scrape_feed("https://solana.com/news/rss", "solana", "solana"),
            self.scrape_feed("https://thedefiant.io/api/feed?tag=solana", "thedefiant", "solana")
        ]
        results = await asyncio.gather(*tasks)
        return [item for sublist in results for item in sublist]

    async def scrape_base_ecosystem(self) -> List[Dict]:
        logger.info("Scraping Base ecosystem...")
        tasks = [
            self.scrape_feed("https://base.mirror.xyz/feed/atom", "base", "base"),
            self.scrape_feed("https://optimism.mirror.xyz/feed/atom", "optimism", "base")
        ]
        results = await asyncio.gather(*tasks)
        return [item for sublist in results for item in sublist]

    async def scrape_web3_research(self) -> List[Dict]:
        logger.info("Scraping Web3 Research...")
        articles = []
        # Arxiv requires specific handling or just use generic feed if RSS compatible
        # For simplicity, using the generic scraper for RSS compatible ones
        sources = [
            ("https://ethresear.ch/latest.rss", "ethresearch"),
            ("https://vitalik.eth.limo/feed.xml", "vitalik"),
            ("https://research.paradigm.xyz/feed.xml", "paradigm")
        ]
        for url, source in sources:
            fetched = await self.scrape_feed(url, source, "research", 5)
            articles.extend(fetched)
            
        # Arxiv manual handling (API)
        try:
            arxiv_url = "http://export.arxiv.org/api/query?search_query=all:blockchain+OR+all:smart+contracts&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending"
            async with self.session.get(arxiv_url) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = feedparser.parse(content)
                    for entry in feed.entries:
                        pub_date = self._parse_date(entry)
                        articles.append({
                            "title": entry.title,
                            "url": entry.link,
                            "summary": entry.summary[:500],
                            "source": "arxiv",
                            "ecosystem_tag": "research",
                            "published_at": pub_date
                        })
        except Exception as e:
            logger.error(f"Arxiv error: {e}")
            
        return articles

    async def scrape_medium_web3(self) -> List[Dict]:
        logger.info("Scraping Medium...")
        url = "https://news.google.com/rss/search?q=site:medium.com+(web3+OR+ethereum+OR+blockchain)+when:7d&hl=en-US&gl=US&ceid=US:en"
        return await self.scrape_feed(url, "medium", "web3", 8)

    async def scrape_all_sources(self) -> List[Dict]:
        tasks = [
            self.scrape_ethereum_blog(),
            self.scrape_farcaster(),
            self.scrape_solana_ecosystem(),
            self.scrape_base_ecosystem(),
            self.scrape_web3_research(),
            self.scrape_medium_web3()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_articles = []
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
        
        # Deduplicate
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        return unique_articles

async def run_scraping_agent():
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    async with Web3ContentScraper() as scraper:
        logger.info("Agent: Starting collection cycle...")
        articles = await scraper.scrape_all_sources()
        
        if not articles:
            logger.warning("Agent: No articles found.")
            return 0
        
        stored_count = 0 
        logger.info(f"Agent: Processing {len(articles)} potential articles...")
        
        for i, article_data in enumerate(articles):
            try:
                # 1. Check if exists
                existing = supabase.table("articles").select("id").eq("url", article_data["url"]).execute()
                if existing.data:
                    continue

                # 2. AI Analysis (Simplified for speed)
                ai_summary = article_data["summary"]
                ai_tag = article_data["ecosystem_tag"]
                ai_legitimacy = 0.5
                ai_sentiment = 5
                
                # Only run AI if summary is missing or tag is generic
                if ai_tag == "web3" or len(ai_summary) < 50:
                    try:
                        logger.info(f"Agent: Analyzing '{article_data['title'][:30]}...'")
                        if i > 0: time.sleep(1)
                        full_text = f"{article_data['title']}\n\n{ai_summary}"
                        ai_analysis = analyze_content(article_data['title'], full_text)
                        if ai_analysis:
                            ai_summary = ai_analysis.get("summary", ai_summary)
                            ai_tag = ai_analysis.get("ecosystem_tag", ai_tag).lower()
                            ai_legitimacy = ai_analysis.get("legitimacy_score", 0.5)
                            ai_sentiment = ai_analysis.get("sentiment_score", 5)
                    except Exception:
                        pass

                # 3. Prepare Final Payload
                db_payload = {
                    "title": article_data["title"],
                    "url": article_data["url"],
                    "source": article_data["source"],
                    "created_at": datetime.now().isoformat(),
                    "summary": ai_summary,
                    "ecosystem_tag": ai_tag.lower(),
                    "published_at": article_data["published_at"], # <--- Using the correctly extracted date
                    "legitimacy_score": ai_legitimacy,
                    "sentiment_score": ai_sentiment,
                    "is_processed": True
                }

                # 4. Save to Supabase
                result = supabase.table("articles").insert(db_payload).execute()
                if result.data:
                    stored_count += 1
                    logger.info(f"Agent: Saved '{article_data['title'][:30]}' as [{ai_tag}]")
                    
            except Exception as e:
                logger.error(f"DB ERROR for {article_data.get('url')}: {e}")
                continue
        
        logger.info(f"Agent Cycle Complete. New Articles: {stored_count}")
        return stored_count