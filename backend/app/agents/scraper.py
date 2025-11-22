import aiohttp
import asyncio
import feedparser
import socket
import logging
import time
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
        # REAL BROWSER HEADERS (Crucial for Medium & Cloudflare protected sites)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
    async def __aenter__(self):
        # FORCE IPv4: Fixes 'getaddrinfo failed' errors on Base/Mirror/Ethereum
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
        """
        Smartly extracts text. Mirror.xyz uses 'content', 
        Medium uses 'summary', others use 'description'.
        """
        content = ""
        if hasattr(entry, 'content'):
            # Atom feeds (Mirror.xyz) often use this
            content = entry.content[0].value
        elif hasattr(entry, 'summary'):
            content = entry.summary
        elif hasattr(entry, 'description'):
            content = entry.description
        
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            return soup.get_text()
        return ""

    def clean_article_content(self, title: str, summary: str) -> tuple[str, str]:
        """Clean and validate article content"""
        clean_title = self.language_filter.clean_text(title)
        clean_summary = self.language_filter.clean_text(summary)
        
        if len(clean_title) > 200:
            clean_title = clean_title[:197] + "..."
        if len(clean_summary) > 3000:
            clean_summary = clean_summary[:2997] + "..."
            
        return clean_title, clean_summary
    
    async def scrape_ethereum_blog(self) -> List[Dict]:
        articles = []
        try:
            logger.info("Scraping Ethereum ecosystem...")
            feeds = [
                "https://blog.ethereum.org/feed.xml",
                "https://newsletter.banklesshq.com/feed" # Added Bankless for more content
            ]
            
            for feed_url in feeds:
                try:
                    async with self.session.get(feed_url) as response:
                        if response.status == 200:
                            content = await response.text()
                            feed = feedparser.parse(content)
                            
                            for entry in feed.entries[:10]:
                                title = entry.title
                                raw_text = self._extract_text_from_entry(entry)
                                
                                if not self.language_filter.should_include_article(title, raw_text):
                                    continue
                                
                                clean_title, clean_summary = self.clean_article_content(title, raw_text)
                                
                                article = {
                                    "title": clean_title,
                                    "url": entry.link,
                                    "summary": clean_summary,
                                    "source": "ethereum",
                                    "ecosystem_tag": "ethereum",
                                    "published_at": datetime.now().isoformat()
                                }
                                articles.append(article)
                except Exception as e:
                    logger.error(f"Error scraping ETH feed {feed_url}: {e}")
            logger.info(f"Found {len(articles)} Ethereum articles")
        except Exception as e:
            logger.error(f"Error in Ethereum scraping: {e}")
        return articles

    async def scrape_farcaster(self) -> List[Dict]:
        articles = []
        try:
            logger.info("Scraping Farcaster blogs...")
            # Using Mirror feeds because they don't require API keys
            feeds = [
                "https://farcaster.mirror.xyz/feed/atom",
                "https://purple.mirror.xyz/feed/atom",
                "https://warpcast.mirror.xyz/feed/atom"
            ]
            
            for feed_url in feeds:
                try:
                    async with self.session.get(feed_url) as response:
                        if response.status == 200:
                            content = await response.text()
                            feed = feedparser.parse(content)
                            
                            for entry in feed.entries[:5]:
                                title = entry.title
                                raw_text = self._extract_text_from_entry(entry)
                                
                                clean_title, clean_summary = self.clean_article_content(title, raw_text)
                                
                                article = {
                                    "title": f"Farcaster: {clean_title}",
                                    "url": entry.link,
                                    "summary": clean_summary,
                                    "source": "farcaster",
                                    "ecosystem_tag": "farcaster",
                                    "published_at": datetime.now().isoformat()
                                }
                                articles.append(article)
                except Exception as e:
                    continue
            logger.info(f"Found {len(articles)} Farcaster articles")
        except Exception as e:
            logger.error(f"Error scraping Farcaster: {e}")
        return articles

    async def scrape_solana_ecosystem(self) -> List[Dict]:
        articles = []
        try:
            logger.info("Scraping Solana ecosystem...")
            feeds = [
                "https://solana.com/news/rss",
                "https://thedefiant.io/api/feed?tag=solana" # Reliable backup
            ]
            
            for feed_url in feeds:
                try:
                    async with self.session.get(feed_url) as response:
                        if response.status == 200:
                            content = await response.text()
                            feed = feedparser.parse(content)
                            
                            for entry in feed.entries[:8]:
                                title = entry.title
                                raw_text = self._extract_text_from_entry(entry)
                                
                                if not self.language_filter.should_include_article(title, raw_text):
                                    continue
                                    
                                clean_title, clean_summary = self.clean_article_content(title, raw_text)
                                
                                article = {
                                    "title": clean_title,
                                    "url": entry.link,
                                    "summary": clean_summary,
                                    "source": "solana",
                                    "ecosystem_tag": "solana",
                                    "published_at": datetime.now().isoformat()
                                }
                                articles.append(article)
                except Exception as e:
                    logger.error(f"Error scraping Solana feed {feed_url}: {e}")
            logger.info(f"Found {len(articles)} Solana articles")
        except Exception as e:
            logger.error(f"Error in Solana scraping: {e}")
        return articles

    async def scrape_base_ecosystem(self) -> List[Dict]:
        articles = []
        try:
            logger.info("Scraping Base ecosystem...")
            feeds = [
                "https://base.mirror.xyz/feed/atom",
                "https://optimism.mirror.xyz/feed/atom"
            ]
            
            for feed_url in feeds:
                try:
                    async with self.session.get(feed_url) as response:
                        if response.status == 200:
                            content = await response.text()
                            feed = feedparser.parse(content)
                            
                            for entry in feed.entries[:8]:
                                title = entry.title
                                raw_text = self._extract_text_from_entry(entry)
                                
                                clean_title, clean_summary = self.clean_article_content(title, raw_text)
                                
                                article = {
                                    "title": clean_title,
                                    "url": entry.link,
                                    "summary": clean_summary,
                                    "source": "base",
                                    "ecosystem_tag": "base",
                                    "published_at": datetime.now().isoformat()
                                }
                                articles.append(article)
                except Exception as e:
                    logger.error(f"Error scraping Base feed {feed_url}: {e}")
            logger.info(f"Found {len(articles)} Base articles")
        except Exception as e:
            logger.error(f"Error in Base scraping: {e}")
        return articles

    async def scrape_web3_research(self) -> List[Dict]:
        articles = []
        try:
            logger.info("Scraping Web3 Research & General...")

            arxiv_url = "http://export.arxiv.org/api/query?search_query=all:blockchain+OR+all:smart+contracts&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending"
            eth_research_url = "https://ethresear.ch/latest.rss"
            vitalik_url = "https://vitalik.eth.limo/feed.xml"
            paradigm_url = "https://research.paradigm.xyz/feed.xml"
            sources = [
                (arxiv_url, "arXiv Research"),
                (eth_research_url, "EthResearch"),
                (vitalik_url, "Vitalik Buterin"),
                (paradigm_url, "Paradigm")
            ]
            
            for url, source_name in sources:
                try:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            content = await response.text()
                            feed = feedparser.parse(content)
                            
                            for entry in feed.entries[:5]:
                                title = entry.title
                                raw_text = self._extract_text_from_entry(entry)
                                
                                # Filter out short/empty comments from forums
                                if len(raw_text) < 50: 
                                    continue

                                clean_title, clean_summary = self.clean_article_content(title, raw_text)
                                
                                # Auto-tagging based on content
                                detected_tag = self._detect_ecosystem(clean_title + " " + clean_summary)
                                if detected_tag == "web3":
                                    detected_tag = "research" # Default to research tag if no specific chain found
                                
                                article = {
                                    "title": clean_title,
                                    "url": entry.link,
                                    "summary": clean_summary,
                                    "source": "research", # Keep source as research for the frontend filter
                                    "ecosystem_tag": detected_tag,
                                    "published_at": datetime.now().isoformat()
                                }
                                articles.append(article)
                except Exception as e:
                    logger.error(f"Error scraping {source_name}: {e}")
                    
            logger.info(f"Found {len(articles)} Research articles")
        except Exception as e:
            logger.error(f"Error in research scraping: {e}")
        return articles

    async def scrape_medium_web3(self) -> List[Dict]:
        articles = []
        try:
            logger.info("Scraping Medium...")
            google_news_url = "https://news.google.com/rss/search?q=site:medium.com+(web3+OR+ethereum+OR+blockchain)+when:7d&hl=en-US&gl=US&ceid=US:en"
            
            async with self.session.get(google_news_url) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = feedparser.parse(content)
                    
                    for entry in feed.entries[:8]:
                        title = entry.title
                        # Google titles often look like "Title - Author Name", let's clean it
                        if " - " in title:
                            title = title.rsplit(" - ", 1)[0]
                            
                        # Google RSS summaries are HTML, clean them
                        raw_text = self._extract_text_from_entry(entry)
                        
                        # Filter low quality
                        if not self.language_filter.should_include_article(title, raw_text):
                            continue

                        clean_title, clean_summary = self.clean_article_content(title, raw_text)
                        
                        article = {
                            "title": clean_title,
                            "url": entry.link, # Google provides a redirect link, which is fine
                            "summary": clean_summary,
                            "source": "medium",
                            "ecosystem_tag": self._detect_ecosystem(clean_title + " " + clean_summary),
                            "published_at": datetime.now().isoformat()
                        }
                        articles.append(article)
                else:
                    logger.warning(f"Google News returned status {response.status}")
                    
            logger.info(f"Found {len(articles)} Medium articles")
        except Exception as e:
            logger.error(f"Medium scraping error: {e}")
        return articles

    def _detect_ecosystem(self, text: str) -> str:
        """Detect ecosystem from text content (Expanded)"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['ethereum', 'eth', 'solidity', 'evm', 'vitalik']):
            return 'ethereum'
        elif any(word in text_lower for word in ['solana', 'sol', 'rust', 'sealevel', 'phantom']):
            return 'solana'
        elif any(word in text_lower for word in ['base network', 'coinbase', 'optimism', 'op stack']):
            return 'base'
        elif any(word in text_lower for word in ['farcaster', 'warpcast', 'frame', 'cast']):
            return 'farcaster'
        elif any(word in text_lower for word in ['bitcoin', 'btc', 'lightning']):
            return 'bitcoin'
        elif any(word in text_lower for word in ['defi', 'uniswap', 'aave', 'lending']):
            return 'defi'
        else:
            return 'web3' 

    def _detect_dao_ecosystem(self, space_id: str) -> str:
        if 'ens' in space_id: return 'ethereum'
        elif 'opcollective' in space_id: return 'optimism'
        return 'web3'

    async def scrape_all_sources(self) -> List[Dict]:
        """Scrape all sources"""
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

                # 2. Prepare Data
                article_text = article_data.get("content") or article_data.get("summary") or ""
                
                # Robust Date Parsing
                raw_date = article_data.get("published_at") or article_data.get("published_date")
                if isinstance(raw_date, str):
                    article_date = raw_date
                elif isinstance(raw_date, datetime):
                    article_date = raw_date.isoformat()
                else:
                    article_date = datetime.utcnow().isoformat()

                # 3. AI Analysis with FALLBACK
                ai_summary = article_text[:500]
                # Force lowercase tag for consistent filtering
                ai_tag = article_data.get("ecosystem_tag", "web3").lower() 
                ai_legitimacy = 0.5
                ai_sentiment = 5
                
                try:
                    logger.info(f"Agent: Thinking about '{article_data['title'][:30]}...'")
                    if i > 0: time.sleep(2) # Rate limit

                    full_text_for_ai = f"{article_data['title']}\n\n{article_text}"
                    ai_analysis = analyze_content(article_data['title'], full_text_for_ai)
                    
                    if ai_analysis:
                        ai_summary = ai_analysis.get("summary", ai_summary)
                        # Force lowercase for the tag
                        ai_tag = ai_analysis.get("ecosystem_tag", ai_tag).lower()
                        ai_legitimacy = ai_analysis.get("legitimacy_score", 0.5)
                        ai_sentiment = ai_analysis.get("sentiment_score", 5)

                except Exception as ai_error:
                    logger.error(f"AI Analysis failed for {article_data['url']}: {ai_error}. Using fallback data.")

                # 4. Prepare Final Payload
                db_payload = {
                    "title": article_data["title"],
                    "url": article_data["url"],
                    "source": article_data["source"],
                    "created_at": article_date,
                    "summary": ai_summary,
                    "ecosystem_tag": ai_tag, # Guaranteed lowercase
                    "legitimacy_score": ai_legitimacy,
                    "sentiment_score": ai_sentiment,
                    "is_processed": True
                }

                # 5. Save to Supabase
                result = supabase.table("articles").insert(db_payload).execute()
                if result.data:
                    stored_count += 1
                    logger.info(f"Agent: Saved '{article_data['title'][:30]}' as [{ai_tag}]")
                    
            except Exception as e:
                logger.error(f"CRITICAL DB ERROR for {article_data.get('url')}: {e}")
                continue
        
        logger.info(f"Agent Cycle Complete. New Articles: {stored_count}")
        return stored_count