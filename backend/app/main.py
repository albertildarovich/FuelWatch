from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from starlette.templating import _TemplateResponse

from app.database import engine, Base
from app.config import get_settings
from app.api import router as api_router
from app.seed_data import seed_database

settings = get_settings()

BASE_DIR = Path(__file__).resolve().parent


# Исправляем баг совместимости Starlette + Jinja2
class FixedJinja2Templates(Jinja2Templates):
    def __init__(self, directory: str) -> None:
        super().__init__(directory=directory)
    
    def TemplateResponse(self, name: str, context: dict, **kwargs: Any) -> _TemplateResponse:
        if "request" not in context:
            raise ValueError("context must include a 'request' key")
        # Передаём globals явно пустым dict, чтобы обойти баг Jinja2
        template = self.get_template(name)
        return _TemplateResponse(
            template=template,
            context=context,
            **kwargs,
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: создаём таблицы и заполняем начальными данными
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed data (только если таблицы пустые)
    await seed_database()
    
    yield
    # Shutdown: закрываем соединения
    await engine.dispose()


app = FastAPI(
    title="FuelWatch",
    description="Сервис мониторинга цен на топливо",
    version="0.1.0",
    lifespan=lifespan,
)

# Static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Templates (Jinja2)
templates = FixedJinja2Templates(directory=str(BASE_DIR / "templates"))

# API роутеры
app.include_router(api_router)


# --- HTML страницы (фронтенд) ---

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return await login_page(request)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/alerts", response_class=HTMLResponse)
async def alerts_page(request: Request):
    return templates.TemplateResponse("alerts.html", {"request": request})


@app.get("/stations", response_class=HTMLResponse)
async def stations_page(request: Request):
    return templates.TemplateResponse("stations.html", {"request": request})
