// ==========================================
// 1. API CONFIGURATION
// ==========================================
// ⚠️ IMPORTANT: Change this to your Ubuntu laptop's IP address!
const BACKEND_URL = "http://192.168.1.50:5000"; 

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
  sendCommand('/trigger-sync'); 
});


// ==========================================
// 3. CHART.JS POWER GRAPH (Live Polling)
// ==========================================
const ctx = document.getElementById('powerChart');
if(ctx) {
  const powerChart = new Chart(ctx.getContext('2d'), {
      type: 'line',
      data: {
          labels: [], 
          datasets: [{
              label: 'Power (mA)',
              data: [], 
              borderColor: '#3b82f6',
              backgroundColor: 'rgba(59, 130, 246, 0.2)',
              borderWidth: 2,
              fill: true,
              tension: 0.3 
          }]
      },
      options: {
          animation: false, 
          scales: { y: { beginAtZero: true, max: 500 } }
      }
  });

  // Pull data from Python every 1 second
  setInterval(async () => {
      try {
          let response = await fetch(`${BACKEND_URL}/get-chart-data`);
          let data = await response.json();
          
          powerChart.data.labels = data.map(row => row.timestamp);
          powerChart.data.datasets[0].data = data.map(row => row.power_mA);
          powerChart.update();
      } catch (error) {
          console.error("Graph Error:", error);
      }
  }, 1000);
}

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