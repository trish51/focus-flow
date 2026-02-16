// This listener only runs once the HTML has fully loaded
document.addEventListener('DOMContentLoaded', function() {

    // Creates a variable for the start button and makes sure it exists
    const startBtn = document.getElementById('start-btn');
    if (!startBtn) return;

    // Creates variables for the timer page
    const display = document.getElementById('timer-display');
    const noteInput = document.getElementById('session-note'); 
    const xpSpan = document.getElementById('xp-count');

    let globalTimerNo = 1;
    let timeLeft = globalTimerNo; 
    let timerId = null;

    // Displays the timer text in a readabile format
    function updateDisplay() {
        let minutes = Math.floor(timeLeft / 60);
        let seconds = timeLeft % 60;
        display.innerText = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
    }

    startBtn.addEventListener('click', () => {
        // Ensures the timer only starts once
        if (timerId) return; 
        
        // Updates the timer every 1 second - refreshes the screen every 1 second
        timerId = setInterval(() => {
            timeLeft--;
            updateDisplay();
            
            // Checks if the timer has run out
            if (timeLeft <= 0) {

                // Stops the 1 seocnd update
                clearInterval(timerId);
                const noteValue = noteInput.value;

                // Gets data (minutes, notes and xp)
                fetch('/log_session', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ 
                        minutes: 25, 
                        note: noteValue
                    })
                }) // Updates data (minutes, notes and xp)
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

    // Pause button - pauses the timer, allowing it to be resumed later
    document.getElementById('pause-btn').addEventListener('click', () => {
        clearInterval(timerId);
        timerId = null;
    });
});