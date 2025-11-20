import re
import logging
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# For consistent results
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)

class LanguageFilter:
    def __init__(self):
        self.english_pattern = re.compile(r'[a-zA-Z]')
        self.non_english_pattern = re.compile(r'[^\x00-\x7F]+')  # Non-ASCII characters
        
    def is_english(self, text: str, min_english_ratio: float = 0.7) -> bool:
        """
        Check if text is primarily English
        Returns True if text is English, False otherwise
        """
        if not text or len(text.strip()) < 10:
            return False
            
        try:
            # Method 1: Character-based check
            clean_text = re.sub(r'\s+', ' ', text.strip())
            if len(clean_text) < 10:
                return False
                
            # Count English characters
            english_chars = len(self.english_pattern.findall(clean_text))
            total_chars = len(clean_text.replace(' ', ''))
            
            if total_chars == 0:
                return False
                
            english_ratio = english_chars / total_chars
            
            # Method 2: langdetect library
            try:
                detected_lang = detect(clean_text)
                is_english_detected = detected_lang == 'en'
            except LangDetectException:
                is_english_detected = False
            
            # Combine both methods
            return english_ratio >= min_english_ratio and is_english_detected
            
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return False
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing special characters and normalizing
        """
        if not text:
            return ""
            
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', text)
        
        # Remove URLs
        clean = re.sub(r'http\S+', '', clean)
        
        # Remove special characters but keep basic punctuation
        clean = re.sub(r'[^\w\s\.\,\!\?\-\:\;\(\)]', '', clean)
        
        # Remove extra whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        # Remove common problematic patterns
        clean = re.sub(r'\.{3,}', '...', clean)  # Normalize ellipsis
        clean = re.sub(r'\u200b', '', clean)  # Remove zero-width spaces
        
        return clean
    
    def should_include_article(self, title: str, summary: str, min_confidence: float = 0.6) -> bool:
        """
        Determine if article should be included based on language
        """
        combined_text = f"{title} {summary}"
        
        # Quick length check
        if len(combined_text.strip()) < 20:
            return False
            
        return self.is_english(combined_text, min_confidence)