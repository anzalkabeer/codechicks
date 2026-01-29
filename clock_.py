import datetime
import time
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

from auth.router import router as auth_router, get_current_admin
from auth.schemas import User
from routers.dashboard import router as dashboard_router
from routers.chat import router as chat_router
from routers.profile import router as profile_router
from routers.admin import router as admin_router
from database.connection import init_db, close_db

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - handles startup and shutdown events."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title="CodeChicks API",
    description="FastAPI backend with auth, dashboard, and global chat",
    version="1.0.0",
    lifespan=lifespan
)

# --- CORS Middleware ---
cors_origins = os.getenv("CORS_ORIGINS", "*")
if cors_origins == "*":
    origins = ["*"]
    # Credentials not allowed with wildcard origin for security
    allow_credentials = False
else:
    origins = [origin.strip() for origin in cors_origins.split(",")]
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(chat_router)
app.include_router(profile_router)
app.include_router(admin_router)

from pathlib import Path

# Base directory for absolute paths
BASE_DIR = Path(__file__).resolve().parent

def serve_html(file_path: str):
    """Helper to serve HTML files with correct path resolution"""
    full_path = BASE_DIR / file_path
    if not full_path.exists():
        return HTMLResponse(content="<h1>404 - Page Not Found</h1>", status_code=404)
    return HTMLResponse(full_path.read_text(encoding="utf-8"))

# Update static mount to use absolute path
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# -- Server-Side Timer State --
class TimerState:
    def __init__(self):
        self.start_time = 0.0
        self.elapsed_time = 0.0
        self.is_running = False

timer_state = TimerState()

class TimerResponse(BaseModel):
    elapsed_time: int  # in milliseconds
    is_running: bool

@app.post("/api/start", response_model=TimerResponse)
async def start_timer():
    if not timer_state.is_running:
        timer_state.start_time = time.time()
        timer_state.is_running = True
    
    # Return current accumulated time (which doesn't change on start, 
    # but we return it for consistency)
    total_ms = int(timer_state.elapsed_time * 1000)
    return TimerResponse(elapsed_time=total_ms, is_running=True)

@app.post("/api/stop", response_model=TimerResponse)
async def stop_timer():
    if timer_state.is_running:
        # Calculate how long it ran since last start
        now = time.time()
        run_duration = now - timer_state.start_time
        timer_state.elapsed_time += run_duration
        timer_state.is_running = False
        timer_state.start_time = 0.0

    total_ms = int(timer_state.elapsed_time * 1000)
    return TimerResponse(elapsed_time=total_ms, is_running=False)

@app.post("/api/reset", response_model=TimerResponse)
async def reset_timer():
    timer_state.start_time = 0.0
    timer_state.elapsed_time = 0.0
    timer_state.is_running = False
    return TimerResponse(elapsed_time=0, is_running=False)

@app.get("/api/status", response_model=TimerResponse)
async def get_timer_status():
    total_elapsed = timer_state.elapsed_time
    if timer_state.is_running:
        total_elapsed += (time.time() - timer_state.start_time)
    
    return TimerResponse(
        elapsed_time=int(total_elapsed * 1000), 
        is_running=timer_state.is_running
    )

# NOTE: /api/dashboard is now handled by routers/dashboard.py with auth protection
@app.get("/", response_class=HTMLResponse)
async def root():
    return serve_html("static/login/login.html")

@app.get("/clock", response_class=HTMLResponse)
async def clock_page():
    return serve_html("static/clock/index.html")

@app.get("/register", response_class=HTMLResponse)
async def register_page():
    return serve_html("static/login/register.html")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    """Serve dashboard UI (mockup)"""
    return serve_html("static/dashboard/index.html")

@app.get("/chat", response_class=HTMLResponse)
async def chat_page():
    """Serve chat UI (mockup)"""
    return serve_html("static/chat/index.html")

@app.get("/onboarding", response_class=HTMLResponse)
async def onboarding_page():
    """Serve onboarding UI (mockup)"""
    return serve_html("static/onboarding/index.html")

@app.get("/settings", response_class=HTMLResponse)
async def settings_page():
    """Serve settings UI"""
    return serve_html("static/settings/index.html")

@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    """Serve admin panel UI"""
    return serve_html("static/admin/index.html")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

