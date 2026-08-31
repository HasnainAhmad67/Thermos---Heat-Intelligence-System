from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from core.exceptions import register_exception_handlers
from routers import assets, heat, risk, scenarios, agent, facility

app = FastAPI(title="THERMOS MVP API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://thermos-heat-intelligence-system-chi.vercel.app",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(assets.router)
app.include_router(heat.router)
app.include_router(risk.router)
app.include_router(scenarios.router)
app.include_router(agent.router)
app.include_router(facility.router)


@app.get("/")
async def root():
    return {"status": "THERMOS MVP backend running"}
