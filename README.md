thermos-mvp/
│
├── README.md
├── .gitignore
├── .env.example
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   │
│   ├── data/
│   │   └── assets.json
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── models.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── asset_service.py
│   │   ├── fortyguard_service.py
│   │   ├── risk_engine.py
│   │   ├── priority_engine.py
│   │   ├── scenario_engine.py
│   │   └── agent_service.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── assets.py
│   │   ├── heat.py
│   │   ├── risk.py
│   │   ├── scenarios.py
│   │   └── agent.py
│   │
│   └── core/
│       ├── __init__.py
│       ├── response.py
│       └── exceptions.py
│
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.ts
    ├── .env.example
    │
    └── src/
        ├── main.tsx
        ├── App.tsx
        │
        ├── api/
        │   └── client.ts
        │
        ├── components/
        │   ├── Dashboard.tsx
        │   ├── HeatPanel.tsx
        │   ├── AssetCard.tsx
        │   ├── RiskPriorityPanel.tsx
        │   ├── ScenarioSimulator.tsx
        │   └── AgentChat.tsx
        │
        ├── types/
        │   └── index.ts
        │
        └── styles/
            └── index.css