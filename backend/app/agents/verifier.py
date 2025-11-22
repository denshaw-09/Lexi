import re
from urllib.parse import urlparse
from datetime import datetime
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class LegitimacyChecker:
    def __init__(self):
        self.scam_keywords = [
            "free", "giveaway", "airdrop", "limited time", "urgent",
            "guaranteed", "100% return", "double your", "secret",
            "don't miss", "last chance", "exclusive", "click here",
            "sign up now", "limited supply", "once in a lifetime" , "discount" 
        ]
        
        self.trusted_authors = [
            "vitalik", "buterin", "paradigm", "a16z", "coinbase",
            "base", "ethereum", "official", "foundation", "solana",
            "farcaster", "snapshot", "governance" 
        ]
        
        self.trusted_domains = [
            "ethereum.org", "blog.ethereum.org", "vitalik.ca",
            "base.org", "docs.base.org", "mirror.xyz",
            "farcaster.xyz", "warpcast.com", "snapshot.org",
            "medium.com", "research.paradigm.xyz", "a16zcrypto.com",
            "solana.com", "solana.org", "solana.foundation",
            "arbitrum.io", "optimism.io", "polygon.technology"
        ]
    
    def check_domain_legitimacy(self, url: str) -> float:
        """Check if domain is trusted"""
        try:
            domain = urlparse(url).netloc.lower()
            
            # Remove www. if present
            if domain.startswith('www.'):
                domain = domain[4:]
            
            for trusted_domain in self.trusted_domains:
                if domain == trusted_domain or domain.endswith('.' + trusted_domain):
                    return 1.0
            
            # Medium publications are generally trusted
            if 'medium.com' in domain:
                return 0.8
                
            # Check for suspicious domains
            if any(suspicious in domain for suspicious in ['.tk', '.ml', '.ga', '.cf']):
                return 0.1
                
            return 0.5  # Neutral score for unknown domains
            
        except Exception as e:
            logger.error(f"Error checking domain: {e}")
            return 0.3
    
    def check_content_quality(self, title: str, summary: str) -> float:
        """Analyze content for scam indicators and quality"""
        score = 1.0
        text = (title + " " + summary).lower()
        
        # Penalize for scam keywords
        scam_count = sum(1 for keyword in self.scam_keywords if keyword in text)
        score -= scam_count * 0.15
        
        # Boost for trusted authors and topics
        author_boost = any(author in text for author in self.trusted_authors)
        if author_boost:
            score += 0.2
        
        # Boost for technical/educational content
        technical_terms = ['tutorial', 'guide', 'explained', 'research', 'analysis', 'technical']
        if any(term in text for term in technical_terms):
            score += 0.1
        
        # Penalize excessive capitalization (common in scams)
        if len(title) > 0 and sum(1 for c in title if c.isupper()) / len(title) > 0.7:
            score -= 0.2
        
        return max(0.1, min(1.0, score))
    
    def check_freshness(self, published_date: datetime) -> float:
        """Check how fresh the content is"""
        try:
            now = datetime.now()
            days_old = (now - published_date).days
            
            if days_old <= 1:
                return 1.0  # Very fresh
            elif days_old <= 7:
                return 0.8  # Recent
            elif days_old <= 30:
                return 0.6  # Somewhat recent
            else:
                return 0.4  # Older content
        except:
            return 0.5  # Neutral if date parsing fails
    
    def check_legitimacy(self, article_data: dict) -> float:
        """Calculate overall legitimacy score for real content"""
        try:
            domain_score = self.check_domain_legitimacy(article_data["url"])
            content_score = self.check_content_quality(article_data["title"], article_data.get("summary", ""))
            
            # Check freshness if published_date is available
            published_date = article_data.get("published_date", datetime.now())
            freshness_score = self.check_freshness(published_date)
            
            # Weighted average with emphasis on domain trust and content quality
            final_score = (domain_score * 0.5) + (content_score * 0.4) + (freshness_score * 0.1)
            
            # Round to 2 decimal places
            return round(final_score, 2)
            
        except Exception as e:
            logger.error(f"Error calculating legitimacy: {e}")
            return 0.5  # Default neutral score