/**
 * CodeChicks Persistent Timer Overlay
 * Handles floating UI, dragging, server sync, and persistence.
 * exact match of logic/UI from clock/index.html
 */

document.addEventListener('DOMContentLoaded', () => {
    injectTimerHTML();
    initTimerLogic();
});

function injectTimerHTML() {
    // Exact structure from static/clock/index.html (Visual Part)
    // Plus a close button manually injected relative to the container
    const html = `
    <div id="floating-timer-overlay">
        <button class="timer-close-btn" id="timer-close" title="Dismiss" style="position: absolute; top: 15px; right: 15px; z-index: 100; font-size: 1.5rem; color: rgba(255,255,255,0.3); background: none; border: none; cursor: pointer; transition: color 0.2s;">×</button>
        
        <div id="clock-container" class="overlay-clone">
            <div id="clock-time">00:00:00</div>
            <div class="controls">
                <button class="ctrl-btn" id="timer-start-btn">START</button>
                <button class="ctrl-btn" id="timer-reset-btn">RESET</button>
            </div>
        </div>
    </div>
    `;
    document.body.insertAdjacentHTML('beforeend', html);
}

function initTimerLogic() {
    const overlay = document.getElementById('floating-timer-overlay');
    // Note: IDs inside duplicate clock-containers might conflict if on clock page?
    // The clock page uses #clock-container. We are injecting another #clock-container.
    // This is bad practice but "literal copy paste" requested.
    // Ideally, we should scope this. But let's select carefully.

    // We select from within our overlay to avoid selecting the page's clock elements if they exist.
    const container = overlay.querySelector('#clock-container');
    const display = overlay.querySelector('#clock-time');
    const startBtn = overlay.querySelector('#timer-start-btn');
    const resetBtn = overlay.querySelector('#timer-reset-btn');
    const closeBtn = document.getElementById('timer-close');

    let timerInterval = null;
    let accumulatedTime = 0; // ms
    let isRunning = false;

    // --- API Interactions ---

    const apiFetch = async (url, method = 'GET') => {
        const token = localStorage.getItem('access_token');
        const headers = { 'Content-Type': 'application/json' };
        if (token) headers['Authorization'] = `Bearer ${token}`;
        try {
            const res = await fetch(url, { method, headers });
            if (res.status === 401) return null;
            return await res.json();
        } catch (e) { console.error(e); return null; }
    };

    const syncState = async () => {
        const data = await apiFetch('/api/status');
        if (!data) return;

        accumulatedTime = data.elapsed_time;
        isRunning = data.is_running;

        updateDisplay(accumulatedTime);
        updateButtons();

        if (isRunning) {
            overlay.classList.add('active');
            startTicking();
        } else {
            stopTicking();
        }
    };

    const startTimer = async () => {
        const res = await apiFetch('/api/start', 'POST');
        if (res) {
            isRunning = true;
            accumulatedTime = res.elapsed_time;
            updateButtons();
            startTicking();
        }
    };

    const stopTimer = async () => {
        const res = await apiFetch('/api/stop', 'POST');
        if (res) {
            isRunning = false;
            accumulatedTime = res.elapsed_time;
            updateDisplay(accumulatedTime);
            updateButtons();
            stopTicking();
        }
    };

    const resetTimer = async () => {
        const res = await apiFetch('/api/reset', 'POST');
        if (res) {
            isRunning = false;
            accumulatedTime = 0;
            updateDisplay(0);
            updateButtons();
            stopTicking();
        }
    };

    // --- Ticking Logic ---
    let tickStartTimestamp = 0;

    function startTicking() {
        if (timerInterval) clearInterval(timerInterval);
        tickStartTimestamp = Date.now();
        const baseTime = accumulatedTime;

        timerInterval = setInterval(() => {
            const delta = Date.now() - tickStartTimestamp;
            updateDisplay(baseTime + delta);
        }, 100);
    }

    function stopTicking() {
        if (timerInterval) clearInterval(timerInterval);
        timerInterval = null;
    }

    // --- UI Helpers ---
    function updateDisplay(ms) {
        const totalSeconds = Math.floor(ms / 1000);
        const h = Math.floor(totalSeconds / 3600);
        const m = Math.floor((totalSeconds % 3600) / 60);
        const s = totalSeconds % 60;
        display.textContent =
            `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    }

    function updateButtons() {
        if (isRunning) {
            startBtn.textContent = 'PAUSE';
            // Use .ctrl-btn .running matching clock css
            startBtn.className = 'ctrl-btn running';
            startBtn.onclick = stopTimer;
        } else {
            startBtn.textContent = 'START';
            startBtn.className = 'ctrl-btn';
            startBtn.onclick = startTimer;
        }
    }

    resetBtn.onclick = resetTimer;

    // --- Dragging Logic ---
    let isDragging = false;
    let initialX, initialY;
    let currentX, currentY;
    let xOffset = 0;
    let yOffset = 0;

    // Make the container the drag handle
    container.addEventListener("mousedown", dragStart);
    document.addEventListener("mouseup", dragEnd);
    document.addEventListener("mousemove", drag);

    function dragStart(e) {
        if (e.target === closeBtn || e.target.tagName === 'BUTTON') return;
        initialX = e.clientX - xOffset;
        initialY = e.clientY - yOffset;
        if (container.contains(e.target)) {
            isDragging = true;
        }
    }

    function dragEnd(e) {
        initialX = currentX;
        initialY = currentY;
        isDragging = false;
    }

    function drag(e) {
        if (isDragging) {
            e.preventDefault();
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
            xOffset = currentX;
            yOffset = currentY;
            setTranslate(currentX, currentY, overlay);
        }
    }

    function setTranslate(xPos, yPos, el) {
        el.style.transform = `translate3d(${xPos}px, ${yPos}px, 0)`;
    }

    // --- Close / Dismiss ---
    closeBtn.onclick = () => {
        overlay.classList.remove('active');
    };

    // Auto-init
    syncState();
    // Poll every 5s
    setInterval(syncState, 5000);
}
