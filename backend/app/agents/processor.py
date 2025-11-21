import google.generativeai as genai
import json
from ..core.config import settings

# Configure Gemini 1.5 Flash (Free & Fast)
genai.configure(api_key=settings.GOOGLE_API_KEY)

def analyze_content(title, raw_text):
    """
    Analyzes text and maps it to the User's specific Database Schema.
    """
    try:
        model = genai.GenerativeModel('models/gemini-flash-latest')
        
        prompt = f"""
        You are Lexi, a Web3 Intelligence Agent. Analyze this article.
        
        Title: {title}
        Content: {raw_text[:4000]} (truncated)
        
        Respond ONLY with a valid JSON object containing:
        1. "summary": A 2-sentence summary.
        2. "sentiment_score": Integer 1-10 (1=Bearish, 10=Bullish).
        3. "ecosystem_tag": One of [Ethereum, Solana, Base, DeFi, NFT, Regulation, General].
        4. "legitimacy_score": Float 0.0 to 1.0 (0.0 = Scam/Spam, 1.0 = Highly Trusted Source).
        """

        response = model.generate_content(prompt)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
        
    except Exception as e:
        print(f"Agent Error: {e}")
        # Fallback data matching your schema
        return {
            "summary": "Analysis unavailable.",
            "sentiment_score": 5,
            "ecosystem_tag": "General",
            "legitimacy_score": 0.5
        }