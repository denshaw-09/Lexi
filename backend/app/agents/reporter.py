import resend
from datetime import datetime, timedelta
from supabase import create_client
from ..core.config import settings

# Use the SERVICE key to ensure we have permissions to read
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
resend.api_key = settings.RESEND_API_KEY

def send_daily_briefing():
    print("Generating Email Report...")
    
    # FIXED: Query for last 2 days to avoid timezone issues
    two_days_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
    
    response = supabase.table("articles")\
        .select("*")\
        .gte("created_at", two_days_ago)\
        .eq("is_processed", True)\
        .order("legitimacy_score", desc=True)\
        .limit(10)\
        .execute()
        
    articles = response.data
    
    if not articles:
        print("No new articles to send.")
        return

    # Build Email (same as before)
    date_str = datetime.now().strftime("%B %d, %Y")
    html = f"<h1>Lexi Intelligence Brief: {date_str}</h1>"
    
    for art in articles:
        trust_badge = "Verified" if art['legitimacy_score'] > 0.8 else "Unverified"
        sentiment = art.get('sentiment_score', 5)
        color = "green" if sentiment >= 7 else "red" if sentiment <= 4 else "orange"

        html += f"""
        <div style="border:1px solid #ddd; padding:15px; margin-bottom:15px; border-radius:8px;">
            <h3 style="margin-top:0;">{art['title']}</h3>
            <div style="font-size:12px; color:#666; margin-bottom:10px;">
                <span style="background:#eee; padding:3px 6px;">{art['ecosystem_tag']}</span>
                <span style="color:{color}; font-weight:bold;"> • Sentiment: {sentiment}/10</span>
                <span> • {trust_badge}</span>
            </div>
            <p>{art['summary']}</p>
            <a href="{art['url']}">Read Source ({art['source']})</a>
        </div>
        """

    try:
        resend.Emails.send({
            "from": "Lexi Agent <onboarding@resend.dev>",
            "to": settings.RECIPIENT_EMAIL,
            "subject": f"Daily Web3 Intel: {len(articles)} Updates",
            "html": html
        })
        print("Email Sent!")
    except Exception as e:
        print(f"Email Error: {e}")