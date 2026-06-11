# Project Structure

```text
EntraLens/
├── app/
│   ├── main.py              # FastAPI routes and dashboard API
│   ├── database.py          # PostgreSQL connection
│   ├── models.py            # SQLAlchemy tables
│   ├── seed.py              # Demo data seeding
│   ├── services/
│   │   ├── ai.py            # Intent detection, Ollama fallback, vision demo
│   │   ├── rag.py           # Demo RAG retrieval
│   │   ├── risk.py          # Risk score logic
│   │   └── mock_azure.py    # Azure mock mapping
│   ├── static/
│   │   ├── style.css        # Premium dashboard UI
│   │   └── app.js           # Frontend logic and charts
│   └── templates/
│       └── index.html       # Dashboard page
├── requirements.txt
├── .env.example
├── .gitignore
├── run.py
└── README.md
```
