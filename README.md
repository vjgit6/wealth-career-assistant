# 💼 Personal Wealth & Career Assistant

A stateful, AI-powered executive wealth and career advisory application running on Google Cloud Vertex AI with **Gemini 3.8 Flash**, built using the **Google Agent Development Kit (ADK)** and an interactive **Browser Web Chat UI**.

---

## 🌟 Key Capabilities

1. **📍 Location-Aware Stock & Equity Intelligence**:
   - Automatically detects user location (defaulting to **Sweden / Stockholm** or dynamically customized).
   - Live quotes and daily performance for regional benchmarks (**OMX Stockholm 30 `^OMX`**, FTSE 100, S&P 500) and regional blue-chips (e.g., `VOLV-B.ST`, `INVE-B.ST`, `AZN.ST`, `ERIC-B.ST`, `SEB-A.ST`) via Yahoo Finance integration.
   - Dynamic currency support (`SEK`, `GBP`, `USD`, `EUR`).

2. **🏠 Deterministic Real Estate Investment Calculator**:
   - Calculates exact fixed-rate mortgages, monthly operating expenses, HOA fees (*BRF avgifter*), Net Operating Income (NOI), **Cap Rate**, and **Cash-on-Cash Return**.
   - Incorporates Nordic and Swedish regulatory real-world context (e.g. *ränteavdrag*, BRF subletting restrictions).

3. **💼 Career & Resume Matching Engine**:
   - Evaluates incoming job opportunities against the user's candidate profile (`data/resume.md`).
   - Generates quantitative match scores (1–10), actionable strengths, and tailored recommendations.

---

## 🏗️ Architecture

```
[ Web Browser ]
      │ (HTTP /chat)
      ▼
[ FastAPI App: frontend/main.py ]  (Port 8080)
      │
      ▼
[ ADK Agent: app/agent.py (Gemini 3.8 Flash) ]
      ├── Tools (`app/tools.py`)
      │     ├─ Location management (SQLite `assistant.db`)
      │     ├─ Live quotes via Yahoo Finance (`yfinance`)
      │     ├─ Real estate ROI formulas (Mortgage, NOI, Cap Rate, CoC)
      │     └─ Resume grounding (`data/resume.md`)
      │
      ▼
[ Vertex AI Agent Runtime ]
```

---

## 🚀 Running Locally

1. **Start the Web Chat App**:
   ```bash
   cd wealth-career-app
   PYTHONPATH=".:$PYTHONPATH" python3 -m uvicorn frontend.main:app --host 0.0.0.0 --port 8080
   ```
2. Open your browser at:
   ```
   http://localhost:8080
   ```

---

## 🧪 Testing with Agents CLI

You can also run or test queries directly via the command line:

```bash
agents-cli run "What is the stock market index in Sweden, and how are Volvo and Ericsson doing?"
```
