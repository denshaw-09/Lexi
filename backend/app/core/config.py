import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "lexi-agent-secret-key")
    
    # Web3 Sources
    FARCASTER_HUB_URL: str = os.getenv("FARCASTER_HUB_URL", "https://hub.pinata.cloud")
    SNAPSHOT_URL: str = os.getenv("SNAPSHOT_URL", "https://snapshot.org")
    MEDIUM_RSS: str = "https://medium.com/feed/tag/web3"
    
    # Whitelisted domains
    WHITELISTED_DOMAINS: list = [
        "ethereum.org", "blog.ethereum.org", "vitalik.ca",
        "base.org", "docs.base.org", "mirror.xyz",
        "farcaster.xyz", "warpcast.com", "snapshot.org",
        "medium.com", "research.paradigm.xyz", "a16zcrypto.com"
    ]

settings = Settings()