let globalTimerNo = 25 * 60;
let timeLeft = globalTimerNo; // 25 minutes in seconds
let timerId = null;

const display = document.getElementById('timer-display');
const startBtn = document.getElementById('start-btn');
const noteInput = document.getElementById('session-note'); 
const xpSpan = document.getElementById('xp-count');

function updateDisplay() {
    let minutes = Math.floor(timeLeft / 60);
    let seconds = timeLeft % 60;
    display.innerText = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
}

startBtn.addEventListener('click', () => {
    if (timerId) return; // Already running
    
    timerId = setInterval(() => {
        timeLeft--;
        updateDisplay();
        
        if (timeLeft <= 0) {
            clearInterval(timerId);
            const noteValue = noteInput.value;

            // Sends data to python
            fetch('/log_session', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ 
                    minutes: 25, 
                    note: noteValue
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success){
                    let currentXP = parseInt(xpSpan.innerText);
                    xpSpan.innerText = currentXP + 10;

                    alert("Awesome! You earned 10 XP!");

                    // Reset Timer for next session
                    timeLeft = globalTimerNo
                    updateDisplay();
                    timerId = null;
                }
            })
        }
    }, 1000);
});

// Pause btn
document.getElementById('pause-btn').addEventListener('click', () => {
    clearInterval(timerId);
    timerId = null;
});