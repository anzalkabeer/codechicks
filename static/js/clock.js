const clockContainer = document.getElementById('clock-container');
const timeDisplay = document.getElementById('clock-time');

// 1. Stopwatch Logic
let startTime = 0;
let elapsedTime = 0;
let timerInterval;
let isRunning = false;

function formatTime(ms) {
    const totalSeconds = Math.floor(ms / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    const pad = (num) => num.toString().padStart(2, '0');
    return `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
}

function updateDisplay() {
    const now = Date.now();
    const timeToShow = isRunning ? (now - startTime + elapsedTime) : elapsedTime;
    timeDisplay.textContent = formatTime(timeToShow);
}

const toggleBtn = document.getElementById('btn-toggle');

// Sync with server on load
let displayIntervalId = null;

async function syncTimerState() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        elapsedTime = data.elapsed_time;
        isRunning = data.is_running;

        if (isRunning) {
            startTime = Date.now();
            if (!displayIntervalId) {
                displayIntervalId = setInterval(updateDisplay, 100);
            }
        } else {
            if (displayIntervalId) {
                clearInterval(displayIntervalId);
                displayIntervalId = null;
            }
        }
        updateDisplay();
        updateButtonState();
    } catch (error) {
        console.error("Failed to sync timer:", error);
    }
}
syncTimerState();
// Poll every 5s to sync with other tabs/overlay
setInterval(syncTimerState, 5000);

function updateButtonState() {
    if (isRunning) {
        toggleBtn.textContent = 'Pause';
        toggleBtn.classList.add('running');
    } else {
        toggleBtn.textContent = 'Start';
        toggleBtn.classList.remove('running');
    }
}

async function toggleTimer() {
    if (isRunning) {
        // Pause
        try {
            const response = await fetch('/api/stop', { method: 'POST' });
            const data = await response.json();

            clearInterval(timerInterval);
            timerInterval = null;
            elapsedTime = data.elapsed_time;
            isRunning = false;
        } catch (error) {
            console.error("Error stopping timer:", error);
        }
    } else {
        // Start
        try {
            const response = await fetch('/api/start', { method: 'POST' });
            const data = await response.json();

            elapsedTime = data.elapsed_time;
            startTime = Date.now();
            if (!timerInterval) {
                timerInterval = setInterval(updateDisplay, 100);
            }
            isRunning = true;
        } catch (error) {
            console.error("Error starting timer:", error);
        }
    }
    updateDisplay();
    updateButtonState();
}

async function resetTimer() {
    try {
        const response = await fetch('/api/reset', { method: 'POST' });
        const data = await response.json();

        clearInterval(timerInterval);
        timerInterval = null;
        isRunning = false;
        elapsedTime = 0;
        startTime = 0;
        timeDisplay.textContent = "00:00:00";
        updateButtonState();
    } catch (error) {
        console.error("Error resetting timer:", error);
    }
}

// 2. Drag Logic
let isDragging = false;
let currentX;
let currentY;
let initialX;
let initialY;
let xOffset = 0;
let yOffset = 0;

clockContainer.addEventListener("mousedown", dragStart);
document.addEventListener("mouseup", dragEnd);
document.addEventListener("mousemove", drag);

function dragStart(e) {
    // Ignore drag if clicking buttons
    if (e.target.tagName === 'BUTTON') return;

    initialX = e.clientX - xOffset;
    initialY = e.clientY - yOffset;

    if (e.target === clockContainer || clockContainer.contains(e.target)) {
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

        setTranslate(currentX, currentY, clockContainer);
    }
}

function setTranslate(xPos, yPos, el) {
    el.style.transform = "translate3d(" + xPos + "px, " + yPos + "px, 0)";
}
