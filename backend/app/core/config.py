from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- Database ---
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SECRET_KEY: str = "lexi-agent-secret-key"
    SUPABASE_SERVICE_KEY: str

    # --- AI & Email ---
    GOOGLE_API_KEY: str
    RESEND_API_KEY: str
    RECIPIENT_EMAIL: str = "ayanakoji08@gmail.com"

    # --- Web3 Sources ---
    FARCASTER_HUB_URL: str = "https://hub.pinata.cloud"
    SNAPSHOT_URL: str = "https://snapshot.org"
    MEDIUM_RSS: str = "https://medium.com/feed/tag/web3"
    
    # --- Whitelisted domains ---
    WHITELISTED_DOMAINS: list = [
        "ethereum.org", "blog.ethereum.org", "vitalik.ca",
        "base.org", "docs.base.org", "mirror.xyz",
        "farcaster.xyz", "medium.com", "research.paradigm.xyz"
    ]

    # This config tells Pydantic to load the .env file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()