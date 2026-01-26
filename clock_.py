import datetime
import time 
from fastapi import FastAPI
import uvicorn
from auth.router import router as auth_router


from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import time

app = FastAPI()

app.include_router(auth_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

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
@app.get("/api/dashboard", response_model=TimerResponse)
async def dashboard():
    return TimerResponse(
        elapsed_time=int(timer_state.elapsed_time * 1000), 
        is_running=timer_state.is_running
    )
@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/login/login.html", "r") as f:
        return f.read()

@app.get("/clock", response_class=HTMLResponse)
async def clock_page():
    with open("static/clock/index.html", "r") as f:
        return f.read()

@app.get("/register", response_class=HTMLResponse)
async def register_page():
    with open("static/login/register.html", "r") as f:
        return f.read()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
