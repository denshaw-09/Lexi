"""
Script to clean existing non-English articles from database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.language_detector import LanguageFilter
from app.core.config import settings
from supabase import create_client

def clean_database():
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    language_filter = LanguageFilter()
    
    # Get all articles
    articles = supabase.table("articles").select("*").execute()
    
    deleted_count = 0
    for article in articles.data:
        title = article['title']
        summary = article.get('summary', '')
        
        if not language_filter.should_include_article(title, summary):
            # Delete non-English article
            supabase.table("articles").delete().eq('id', article['id']).execute()
            deleted_count += 1
            print(f"Deleted non-English article: {title[:50]}...")
    
    print(f"Cleaned {deleted_count} non-English articles from database")

if __name__ == "__main__":
    clean_database()