# Lexi Agent: AI-Powered Web3 Intelligence Engine

**Lexi Agent** is an autonomous, AI-driven content aggregator and analysis engine designed specifically for the Web3 ecosystem. 

Unlike standard news aggregators that flood you with price hype and noise, Lexi reads, understands, and scores technical developments across blockchain ecosystems in real-time. It is designed for developers, researchers, and serious investors who care about **signal over noise**.

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase)
![Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini-8E75B2?style=for-the-badge&logo=google)
---

## What Does Lexi Do?

Lexi acts as a 24/7 research assistant that monitors the pulse of the decentralized web. It autonomously:
Scouts: Crawls high-value technical sources (Ethereum Research, Arxiv, Foundation Blogs, Farcaster).
Analyzes: Uses Large Language Models (Google Gemini) to read articles, extract key insights, and determine market sentiment.

---

## Real-World Utility

The Web3 space generates thousands of articles daily. 99% of it is price speculation or low-quality clickbait.

**Lexi solves the "Information Overload" problem:**
*   **For Developers:** Never miss a critical EIP (Ethereum Improvement Proposal) or a breaking change in the Base/Optimism stack.
*   **For Investors:** Get a sentiment score on the actual *technology* being built, not just market sentiment.
*   **For Researchers:** Automatically discover new academic papers on Zero Knowledge Proofs or Consensus mechanisms from Arxiv without manual searching.

---

## What Sets Lexi Apart?

| Feature | Standard News Aggregators | 🧠 Lexi Agent |
| :--- | :--- | :--- |
| **Data Source** | Mainstream Crypto News (CoinDesk, etc.) | **Technical Sources** (EthResearch, Arxiv, Dev Blogs) |
| **Processing** | Keyword matching | **LLM Semantic Analysis** (Gemini AI) |
| **Filtering** | None (Clickbait included) | **Sentiment & Quality Scoring** |
| **Auth** | Email only | **Wallet (SIWE) + Web2 Hybrid** |
| **Focus** | Price Action | **Protocol Development & Research** |

---

## Key Features

### 1. Multi-Chain Ecosystem Monitoring
Lexi employs specialized scrapers to monitor high-value technical sources:
*   **Ethereum Core:** `ethresear.ch`, Ethereum Foundation Blog.
*   **L2 Ecosystems:** Optimism Governance, Base Protocol updates.
*   **Academic Research:** Arxiv (Cryptography & Blockchain categories).
*   **Social Signal:** Farcaster and Medium engineering blogs.

### 2. AI-Driven Analysis
*   **Automated Summarization:** Condenses complex whitepapers into readable insights.
*   **Sentiment Scoring:** Assigns a numerical score to articles based on technical optimism vs. pessimism.
*   **Context Awareness:** Distinguishes between a "marketing partnership" and a "protocol upgrade."

### 3. Hybrid Authentication (Web3 Native)
*   **Wallet Login:** Secure authentication using Ethereum signatures (SIWE standard).
*   **Traditional Auth:** Full support for Email/Password and Google OAuth.

### 4. Robust Scheduling
*   **Smart Polling:** Dual-schedule system (Quick updates every 30 mins, Deep scrapes every 6 hours).
*   **Deduplication:** Intelligent database logic prevents duplicate content processing.

---

## Technical Architecture

*   **Backend:** Python (FastAPI) for high-performance async API handling.
*   **Database:** Supabase (PostgreSQL) with `pgvector` support for future RAG implementations.
*   **AI Engine:** Google Gemini (Generative AI) for content processing.
*   **Web3:** `Web3.py` for cryptographic signature verification and address validation.
*   **Scraping:** `HTTPX` (Async) + `BeautifulSoup4`.

---

## Getting Started

### Prerequisites
*   Python 3.10+
*   Supabase 
*   Google Gemini API Key

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/lexi-agent.git
```
```
cd lexi-agent/backend
```
### 2. Install Dependencies
```bash

python -m venv venv

# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt

# Ensure httpx is up to date for Supabase compatibility
pip install --upgrade httpx httpcore
```

### 3. Environment Variables
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
GEMINI_API_KEY=your_google_gemini_key
SECRET_KEY=your_jwt_secret_key
```

### 5. Run the Server
```
uvicorn app.main:app --reload
```
The API will be available at http://127.0.0.1:8000.

## Roadmap

- [ ] Vector Search (RAG): Chat with the database to ask questions like "What are the latest updates on Optimism governance?"

- [ ] On-Chain Actions: Execute transactions based on specific proposal outcomes.

- [ ] Personalized Feeds: AI-curated digests based on user wallet history.