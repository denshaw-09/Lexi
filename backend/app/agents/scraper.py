import aiohttp
import asyncio
import feedparser
import json
import logging
from datetime import datetime
from typing import List, Dict
from bs4 import BeautifulSoup
from app.core.config import settings
from .language_detector import LanguageFilter  # Add this import

logger = logging.getLogger(__name__)

class Web3ContentScraper:
    def __init__(self):
        self.session = None
        self.language_filter = LanguageFilter()  # Add language filter
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers=self.headers
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    
    def clean_article_content(self, title: str, summary: str) -> tuple[str, str]:
        """Clean and validate article content"""
        clean_title = self.language_filter.clean_text(title)
        clean_summary = self.language_filter.clean_text(summary)
        
        # Ensure reasonable length
        if len(clean_title) > 200:
            clean_title = clean_title[:197] + "..."
        if len(clean_summary) > 500:
            clean_summary = clean_summary[:497] + "..."
            
        return clean_title, clean_summary
    
    async def scrape_medium_web3(self) -> List[Dict]:
        """Scrape real Medium Web3 articles with language filtering"""
        articles = []
        try:
            logger.info("Scraping real Medium Web3 articles...")
            
            medium_feeds = [
                "https://medium.com/feed/tag/web3",
                "https://medium.com/feed/tag/blockchain",
                "https://medium.com/feed/tag/ethereum",
                "https://medium.com/feed/tag/defi",
                "https://medium.com/feed/tag/solana",
                "https://medium.com/feed/tag/cryptocurrency"
            ]
            
            for feed_url in medium_feeds:
                try:
                    async with self.session.get(feed_url) as response:
                        if response.status == 200:
                            content = await response.text()
                            feed = feedparser.parse(content)
                            
                            for entry in feed.entries[:15]:
                                # Clean and validate content
                                title = entry.title
                                raw_summary = entry.get('summary', '')
                                
                                # Clean HTML from summary
                                if raw_summary:
                                    soup = BeautifulSoup(raw_summary, 'html.parser')
                                    raw_summary = soup.get_text()
                                
                                # Check if content is English
                                if not self.language_filter.should_include_article(title, raw_summary):
                                    logger.debug(f"🔍 Skipping non-English article: {title[:50]}...")
                                    continue
                                
                                # Clean the content
                                clean_title, clean_summary = self.clean_article_content(title, raw_summary)
                                
                                article = {
                                    "title": clean_title,
                                    "url": entry.link,
                                    "summary": clean_summary or "Web3 content from Medium",
                                    "source": "medium",
                                    "ecosystem_tag": self._detect_ecosystem(clean_title + " " + clean_summary),
                                    "published_date": datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') and entry.published_parsed else datetime.now()
                                }
                                articles.append(article)
                                
                except Exception as e:
                    logger.error(f"Error scraping Medium feed {feed_url}: {e}")
                    continue
            
            logger.info(f"Found {len(articles)} English Medium articles")
            
        except Exception as e:
            logger.error(f"Error in Medium scraping: {e}")
        return articles
    
    async def scrape_ethereum_blog(self) -> List[Dict]:
        """Scrape real Ethereum Foundation blog"""
        articles = []
        try:
            logger.info("Scraping real Ethereum Foundation blog...")
            
            ethereum_feeds = [
                "https://blog.ethereum.org/feed.xml",
                "https://ethereum.org/en/feed.xml"
            ]
            
            for feed_url in ethereum_feeds:
                try:
                    async with self.session.get(feed_url) as response:
                        if response.status == 200:
                            content = await response.text()
                            feed = feedparser.parse(content)
                            
                            for entry in feed.entries[:15]:
                                title = entry.title
                                summary = entry.get('summary', '')[:300] + "..." if len(entry.get('summary', '')) > 300 else entry.get('summary', 'Ethereum update')
                                
                                # Ethereum blog is always English, but let's validate
                                if not self.language_filter.should_include_article(title, summary):
                                    continue
                                
                                clean_title, clean_summary = self.clean_article_content(title, summary)
                                
                                article = {
                                    "title": clean_title,
                                    "url": entry.link,
                                    "summary": clean_summary,
                                    "source": "ethereum",
                                    "ecosystem_tag": "ethereum",
                                    "published_date": datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') and entry.published_parsed else datetime.now()
                                }
                                articles.append(article)
                                
                except Exception as e:
                    logger.error(f"Error scraping Ethereum feed {feed_url}: {e}")
                    continue
            
            logger.info(f"Found {len(articles)} English Ethereum articles")
            
        except Exception as e:
            logger.error(f"Error in Ethereum blog scraping: {e}")
        return articles
    
    async def scrape_farcaster(self) -> List[Dict]:
        """Scrape real Farcaster data using Neynar API"""
        articles = []
        try:
            logger.info("Scraping real Farcaster data...")
            
            # Using Neynar API for Farcaster data
            neynar_url = "https://api.neynar.com/v2/farcaster/feed/trending?limit=20"
            headers = {
                'api_key': 'NEYNAR_API_DOCS'
            }
            
            async with self.session.get(neynar_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for cast in data.get('casts', [])[:15]:
                        if cast.get('text') and len(cast['text']) > 50:
                            title = f"Farcaster: {cast['author']['username']}"
                            summary = cast['text']
                            
                            # Filter English content
                            if not self.language_filter.should_include_article(title, summary, min_confidence=0.5):
                                continue
                                
                            clean_title, clean_summary = self.clean_article_content(title, summary)
                            
                            article = {
                                "title": clean_title,
                                "url": f"https://warpcast.com/{cast['author']['username']}/{cast['hash']}",
                                "summary": clean_summary,
                                "source": "farcaster",
                                "ecosystem_tag": "farcaster",
                                "published_date": datetime.fromtimestamp(cast['timestamp'] / 1000) if cast.get('timestamp') else datetime.now()
                            }
                            articles.append(article)
                
                else:
                    # Fallback with language filtering
                    await self._scrape_farcaster_fallback(articles)
            
            logger.info(f"Found {len(articles)} English Farcaster casts")
            
        except Exception as e:
            logger.error(f"Error scraping Farcaster: {e}")
            await self._scrape_farcaster_fallback(articles)
            
        return articles
    
    async def _scrape_farcaster_fallback(self, articles: List[Dict]):
        """Fallback Farcaster scraping with language filtering"""
        try:
            # This would be your fallback implementation
            # For now, skip since we want real English content
            pass
        except Exception as e:
            logger.error(f"Farcaster fallback also failed: {e}")
    
    async def scrape_snapshot_proposals(self) -> List[Dict]:
        """Scrape real Snapshot governance proposals"""
        articles = []
        try:
            logger.info("Scraping real Snapshot proposals...")
            
            snapshot_url = "https://hub.snapshot.org/graphql"
            
            queries = [
                {
                    "query": """
                    query {
                      proposals (
                        first: 10,
                        skip: 0,
                        where: { space_in: ["ens.eth", "aave.eth", "uniswap"] },
                        orderBy: "created",
                        orderDirection: desc
                      ) {
                        id
                        title
                        body
                        start
                        end
                        snapshot
                        state
                        author
                        space {
                          id
                          name
                        }
                      }
                    }
                    """
                }
            ]
            
            for query in queries:
                try:
                    async with self.session.post(snapshot_url, json=query) as response:
                        if response.status == 200:
                            data = await response.json()
                            proposals = data.get('data', {}).get('proposals', [])
                            
                            for proposal in proposals:
                                title = f"Governance: {proposal['title']}"
                                body = proposal.get('body', '')
                                summary = body[:250] + "..." if len(body) > 250 else body
                                
                                # Snapshot proposals are usually English, but validate
                                if not self.language_filter.should_include_article(title, body):
                                    continue
                                    
                                clean_title, clean_summary = self.clean_article_content(title, summary)
                                
                                article = {
                                    "title": clean_title,
                                    "url": f"https://snapshot.org/#/{proposal['space']['id']}/proposal/{proposal['id']}",
                                    "summary": clean_summary or f"Governance proposal for {proposal['space']['name']}",
                                    "source": "snapshot",
                                    "ecosystem_tag": self._detect_dao_ecosystem(proposal['space']['id']),
                                    "published_date": datetime.fromtimestamp(proposal['start'])
                                }
                                articles.append(article)
                                
                except Exception as e:
                    logger.error(f"Error in Snapshot query: {e}")
                    continue
            
            logger.info(f"Found {len(articles)} English Snapshot proposals")
            
        except Exception as e:
            logger.error(f"Error scraping Snapshot: {e}")
        return articles
    
    async def scrape_solana_ecosystem(self) -> List[Dict]:
        """Scrape real Solana ecosystem content"""
        articles = []
        try:
            logger.info("Scraping real Solana ecosystem...")
            
            solana_feeds = [
                "https://solana.com/news/rss",
                "https://solana.ghost.io/rss/"
            ]
            
            for feed_url in solana_feeds:
                try:
                    async with self.session.get(feed_url) as response:
                        if response.status == 200:
                            content = await response.text()
                            feed = feedparser.parse(content)
                            
                            for entry in feed.entries[:10]:
                                title = entry.title
                                summary = entry.get('summary', '')[:300] + "..." if len(entry.get('summary', '')) > 300 else entry.get('summary', 'Solana ecosystem update')
                                
                                if not self.language_filter.should_include_article(title, summary):
                                    continue
                                    
                                clean_title, clean_summary = self.clean_article_content(title, summary)
                                
                                article = {
                                    "title": clean_title,
                                    "url": entry.link,
                                    "summary": clean_summary,
                                    "source": "solana",
                                    "ecosystem_tag": "solana",
                                    "published_date": datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') and entry.published_parsed else datetime.now()
                                }
                                articles.append(article)
                                
                except Exception as e:
                    logger.error(f"Error scraping Solana feed {feed_url}: {e}")
                    continue
            
            logger.info(f"Found {len(articles)} English Solana articles")
            
        except Exception as e:
            logger.error(f"Error in Solana scraping: {e}")
        return articles
    
    async def scrape_base_ecosystem(self) -> List[Dict]:
        """Scrape real Base ecosystem content"""
        articles = []
        try:
            logger.info("Scraping real Base ecosystem...")
            
            base_feeds = [
                "https://base.org/blog/rss.xml",
            ]
            
            for feed_url in base_feeds:
                try:
                    async with self.session.get(feed_url) as response:
                        if response.status == 200:
                            content = await response.text()
                            feed = feedparser.parse(content)
                            
                            for entry in feed.entries[:10]:
                                title = entry.title
                                summary = entry.get('summary', '')[:300] + "..." if len(entry.get('summary', '')) > 300 else entry.get('summary', 'Base ecosystem update')
                                
                                if not self.language_filter.should_include_article(title, summary):
                                    continue
                                    
                                clean_title, clean_summary = self.clean_article_content(title, summary)
                                
                                article = {
                                    "title": clean_title,
                                    "url": entry.link,
                                    "summary": clean_summary,
                                    "source": "base",
                                    "ecosystem_tag": "base",
                                    "published_date": datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') and entry.published_parsed else datetime.now()
                                }
                                articles.append(article)
                                
                except Exception as e:
                    logger.error(f"Error scraping Base feed {feed_url}: {e}")
                    continue
            
            logger.info(f"Found {len(articles)} English Base articles")
            
        except Exception as e:
            logger.error(f"Error in Base scraping: {e}")
        return articles
    
    async def scrape_web3_research(self) -> List[Dict]:
        """Scrape real Web3 research papers and technical content"""
        articles = []
        try:
            logger.info("Scraping real Web3 research...")
            
            research_sources = [
                "https://research.paradigm.xyz/feed.xml",
                "https://a16zcrypto.com/feed/",
                "https://variant.fund/feed/",
            ]
            
            for feed_url in research_sources:
                try:
                    async with self.session.get(feed_url) as response:
                        if response.status == 200:
                            content = await response.text()
                            feed = feedparser.parse(content)
                            
                            for entry in feed.entries[:8]:
                                title = entry.title
                                summary = entry.get('summary', '')[:350] + "..." if len(entry.get('summary', '')) > 350 else entry.get('summary', 'Web3 research content')
                                
                                if not self.language_filter.should_include_article(title, summary):
                                    continue
                                    
                                clean_title, clean_summary = self.clean_article_content(title, summary)
                                
                                article = {
                                    "title": clean_title,
                                    "url": entry.link,
                                    "summary": clean_summary,
                                    "source": "research",
                                    "ecosystem_tag": self._detect_ecosystem(clean_title + " " + clean_summary),
                                    "published_date": datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') and entry.published_parsed else datetime.now()
                                }
                                articles.append(article)
                                
                except Exception as e:
                    logger.error(f"Error scraping research feed {feed_url}: {e}")
                    continue
            
            logger.info(f"Found {len(articles)} English research articles")
            
        except Exception as e:
            logger.error(f"Error in research scraping: {e}")
        return articles
    
    def _detect_ecosystem(self, text: str) -> str:
        """Detect ecosystem from text content"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['ethereum', 'eth', 'solidity', 'evm']):
            return 'ethereum'
        elif any(word in text_lower for word in ['solana', 'sol', 'rust', 'sealevel']):
            return 'solana'
        elif any(word in text_lower for word in ['base', 'coinbase', 'optimism']):
            return 'base'
        elif any(word in text_lower for word in ['farcaster', 'warpcast', 'cast']):
            return 'farcaster'
        elif any(word in text_lower for word in ['bitcoin', 'btc', 'lightning']):
            return 'bitcoin'
        elif any(word in text_lower for word in ['polygon', 'matic', 'pos']):
            return 'polygon'
        elif any(word in text_lower for word in ['arbitrum', 'rollup']):
            return 'arbitrum'
        else:
            return 'web3'
    
    def _detect_dao_ecosystem(self, space_id: str) -> str:
        """Detect ecosystem from DAO space ID"""
        if 'ens' in space_id:
            return 'ethereum'
        elif 'aave' in space_id:
            return 'defi'
        elif 'uniswap' in space_id:
            return 'defi'
        elif 'compound' in space_id:
            return 'defi'
        elif 'maker' in space_id:
            return 'defi'
        elif 'opcollective' in space_id:
            return 'optimism'
        else:
            return 'web3'
    
    async def scrape_all_sources(self) -> List[Dict]:
        """Scrape all real sources with language filtering"""
        tasks = [
            self.scrape_medium_web3(),
            self.scrape_ethereum_blog(),
            self.scrape_farcaster(),
            self.scrape_snapshot_proposals(),
            self.scrape_solana_ecosystem(),
            self.scrape_base_ecosystem(),
            self.scrape_web3_research()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_articles = []
        for i, result in enumerate(results):
            if isinstance(result, list):
                all_articles.extend(result)
                logger.info(f"Source {i} contributed {len(result)} English articles")
            else:
                logger.error(f"Source {i} failed: {result}")
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        logger.info(f"Total unique English articles scraped: {len(unique_articles)}")
        return unique_articles

# Background agent runner
async def run_scraping_agent():
    """Main function to run the real scraping agent with language filtering"""
    async with Web3ContentScraper() as scraper:
        articles = await scraper.scrape_all_sources()
        
        if not articles:
            logger.warning("No English articles scraped from any source")
            return 0
        
        # Check legitimacy and store in database
        from .verifier import LegitimacyChecker
        from app.models.schemas import ArticleCreate
        from supabase import create_client
        from app.core.config import settings
        
        checker = LegitimacyChecker()
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        
        stored_count = 0
        for article_data in articles:
            try:
                legitimacy_score = checker.check_legitimacy(article_data)
                
                # Store all English articles
                article = ArticleCreate(
                    title=article_data["title"][:500],
                    url=article_data["url"],
                    summary=article_data.get("summary", "")[:1000],
                    source=article_data["source"],
                    ecosystem_tag=article_data["ecosystem_tag"],
                    legitimacy_score=legitimacy_score
                )
                
                # Check if article already exists
                existing = supabase.table("articles").select("id").eq("url", article.url).execute()
                
                if not existing.data:
                    result = supabase.table("articles").insert(article.dict()).execute()
                    if result.data:
                        stored_count += 1
                        logger.info(f"Stored English article: {article.title[:60]}... (Score: {legitimacy_score})")
                    else:
                        logger.warning(f"Failed to store: {article.title[:60]}")
                else:
                    logger.info(f"Already exists: {article.title[:60]}")
                    
            except Exception as e:
                logger.error(f"Error storing article: {e}")
                continue
        
        logger.info(f"Successfully stored {stored_count} new English articles in database")
        return stored_count