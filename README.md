# AI Paper Trading Platform

An AI-assisted **paper trading platform** designed to simulate stock market trading while providing intelligent decision support using machine learning and natural language processing.

This project is built as a **research, learning, and prototyping platform** for algorithmic trading, AI-driven stock analysis, and portfolio management — without using real money.

---

## 🚀 Project Overview

The platform allows users to:

- Trade stocks using **virtual capital** (paper trading)
- Maintain portfolios, positions, and trade history
- Analyze market data using indicators
- Use AI to assist with:
  - Stock screening
  - Pattern recognition
  - Strategy selection
  - Trade decision support

The long-term vision is to evolve this system into an **AI trading intelligence layer** that can integrate with real broker or institutional systems.

---

## 🧠 Core Features

### Current / Planned Capabilities
- Virtual trading account with configurable balance
- Buy and sell stocks (paper trades)
- Portfolio and P&L tracking
- REST API backend
- Modular architecture for AI and strategies

### AI-Oriented Capabilities (Planned)
- Technical indicator analysis (RSI, EMA, MACD, etc.)
- Natural-language stock filtering
- Chart pattern recognition
- Strategy-based trade automation (simulation only)
- Backtesting engine

---

## 🏗️ Project Architecture
```
 AI Paper Trading/
├─ backend/
│ ├─ main.py
│ ├─ core/ # Config, database, redis
│ ├─ api/ # API routes
│ ├─ trading/ # Paper trading logic
│ ├─ indicators/ # Technical indicators
│ ├─ ai/ # AI / LLM integration
│ ├─ strategies/ # Trading strategies
│ └─ backtesting/ # Backtesting engine
├─ .env # Environment variables (not committed)
└─ README.md
```

---

## 🛠️ Tech Stack

### Backend
- **Python 3.11**
- **FastAPI**
- **SQLAlchemy**
- **PostgreSQL**
- **Redis**

### AI / ML
- **Ollama** (local LLM inference)
- **PyTorch / scikit-learn** (planned)
- **Pandas / NumPy**

### Frontend (Planned)
- **Next.js**
- **TypeScript**
- **TradingView Lightweight Charts**

---

## ▶️ Running the Backend (Development)

From the project root:

```bash
source backend/.venv/bin/activate.fish
uvicorn backend.main:app --reload
```

Then open:

http://127.0.0.1:8000

---

## ⚠️ Disclaimer

This project is for educational and research purposes only.

- No real money is used
- No financial advice is provided
- Trading logic is experimental
- Past performance does not imply future results

---

## 🚧 Work in Progress

This project is currently under active development.

Ongoing work includes:

- Expanding trading APIs
- Adding technical indicator calculations
- Integrating AI-powered stock screening
- Improving database design and scalability
- Building a frontend dashboard
- Adding backtesting and strategy evaluation

APIs, schemas, and features may change as the project evolves.

---

## 📌 Future Roadmap

- Multi-user support
- Authentication and authorization
- Advanced AI strategy optimization
- Broker API integrations (optional)
- Enterprise-grade analytics and reporting

---

## 📄 License

This project is currently not licensed for commercial use.
Licensing terms will be added in the future.

---
