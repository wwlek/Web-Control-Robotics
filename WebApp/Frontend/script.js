// ==========================================
// 1. API CONFIGURATION
// ==========================================
// ⚠️ IMPORTANT: Change this to your Ubuntu laptop's IP address!
const BACKEND_URL = "http://localhost:5000"; 

// A helper function to easily send POST commands to Python
async function sendCommand(endpoint, payload = null) {
  try {
      let options = { method: 'POST' };
      if (payload) {
          options.headers = { 'Content-Type': 'application/json' };
          options.body = JSON.stringify(payload);
      }
      const response = await fetch(`${BACKEND_URL}${endpoint}`, options);
      return await response.json();
  } catch (error) {
      console.error(`Failed to reach ${endpoint}:`, error);
  }
}


// ==========================================
// 2. EXISTING UI LOGIC + API CALLS
// ==========================================
document.querySelectorAll('.card').forEach(card => {
  const stopBtn = card.querySelector('.toggle.stop');
  const danceBtn = card.querySelector('.toggle.dance');
  const catId = card.dataset.cat; // Gets the data-cat="1" from HTML

  if(stopBtn && danceBtn) {
    stopBtn.addEventListener('click', () => {
      const isActive = stopBtn.classList.toggle('active');
      card.classList.toggle('disabled', isActive);

      if (isActive) {
        danceBtn.classList.remove('active');
        // SEND API COMMAND: Tell specific cat to stop
        if(catId) sendCommand('/cat-command', { cat_id: parseInt(catId), action: "stop" });
      }
    });

    danceBtn.addEventListener('click', () => {
      if (card.classList.contains('disabled')) return;
      danceBtn.classList.toggle('active');
      
      // SEND API COMMAND: Tell specific cat to dance
      if(catId) sendCommand('/cat-command', { cat_id: parseInt(catId), action: "dance" });
    });
  }

  // Hook up the directional arrows
  card.querySelectorAll('.btn').forEach(arrowBtn => {
    arrowBtn.addEventListener('click', () => {
      const direction = arrowBtn.dataset.action;
      if(catId) sendCommand('/cat-command', { cat_id: parseInt(catId), action: direction });
    });
  });
});

// GLOBAL BUTTONS
document.getElementById('all-stop')?.addEventListener('click', () => {
  document.querySelectorAll('.card:not(.global-control)').forEach(card => {
    card.classList.add('disabled');
    card.querySelector('.toggle.stop')?.classList.add('active');
    card.querySelector('.toggle.dance')?.classList.remove('active');
  });
  // API CALL: Tell backend to stop everything
  sendCommand('/trigger-stop-all'); 
});

document.getElementById('all-dance')?.addEventListener('click', () => {
  document.querySelectorAll('.card:not(.global-control)').forEach(card => {
    if (card.classList.contains('disabled')) return;
    card.querySelector('.toggle.dance')?.classList.add('active');
  });
  // API CALL: This hits the endpoint we already built in Python!
  sendCommand('/trigger-dance'); 
});

// ==========================================
// 3. CHART.JS INDIVIDUAL MINI-GRAPHS
// ==========================================
const catCharts = {}; // This will hold our 4 separate charts
const chartColors = { 1: '#ef4444', 2: '#facc15', 3: '#22c55e', 4: '#3b82f6' };

// Initialize a mini-chart for each of the 4 cats
[1, 2, 3, 4].forEach(id => {
    const ctx = document.getElementById(`chart-cat-${id}`);
    if (ctx) {
        catCharts[id] = new Chart(ctx.getContext('2d'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    borderColor: chartColors[id],
                    backgroundColor: chartColors[id] + '33', // Adds transparency to the fill
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0 // Hides the ugly dots for a clean "sparkline" look
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                plugins: {
                    legend: { display: false } // Hide the legend to save space
                },
                scales: {
                    x: { display: false }, // Hide the time labels on the bottom to save space
                    y: { beginAtZero: true, max: 600, ticks: { maxTicksLimit: 4 } }
                }
            }
        });
    }
});

// Pull data from Python every 1 second and route it to the correct chart
setInterval(async () => {
    try {
        let response = await fetch(`${BACKEND_URL}/get-chart-data`);
        let data = await response.json();
        
        // Get all unique timestamps chronologically
        let timeLabels = [...new Set(data.map(row => row.timestamp))].sort();

        // Update each chart with its specific data
        [1, 2, 3, 4].forEach(id => {
            if (!catCharts[id]) return;

            // Create an empty array for this cat's timeline
            let catData = new Array(timeLabels.length).fill(null);
            
            // Fill in the power numbers at the correct time slots
            data.forEach(row => {
                if (row.cat_id === id) {
                    let timeIndex = timeLabels.indexOf(row.timestamp);
                    catData[timeIndex] = row.power_mA;
                }
            });

            // Push the new data to the chart
            catCharts[id].data.labels = timeLabels;
            catCharts[id].data.datasets[0].data = catData;
            catCharts[id].update();
        });
        
    } catch (error) {
        console.error("Graph Error:", error);
    }
}, 1000);

// Akkuanzeige initialisieren (Kept exactly as you wrote it)
document.querySelectorAll('.battery').forEach(battery => {
  const level = Number(battery.dataset.level);
  const fill = battery.querySelector('.battery-fill');
  const text = battery.querySelector('.battery-text');
  fill.style.width = level + '%';
  text.textContent = level + '%';
  fill.classList.remove('green', 'yellow', 'red');
  if (level > 60) { fill.classList.add('green'); } 
  else if (level > 30) { fill.classList.add('yellow'); } 
  else { fill.classList.add('red'); }
});