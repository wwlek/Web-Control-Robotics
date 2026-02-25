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
  sendCommand('/trigger-sync'); 
});

// ==========================================
// 3. CHART.JS MULTI-CAT GRAPH
// ==========================================
const ctx = document.getElementById('powerChart');
if(ctx) {
  const powerChart = new Chart(ctx.getContext('2d'), {
      type: 'line',
      data: {
          labels: [], // Time (X-axis)
          datasets: [
              { label: 'Cat 1', data: [], borderColor: '#ef4444', tension: 0.3 }, // Red
              { label: 'Cat 2', data: [], borderColor: '#facc15', tension: 0.3 }, // Yellow
              { label: 'Cat 3', data: [], borderColor: '#22c55e', tension: 0.3 }, // Green
              { label: 'Cat 4', data: [], borderColor: '#3b82f6', tension: 0.3 }  // Blue
          ]
      },
      options: {
          responsive: true,               // Make it resize
          maintainAspectRatio: false,     // THE MAGIC LINE: Stop forcing a square shape!
          animation: false, 
          scales: { y: { beginAtZero: true, max: 600 } }
      }
  });

  // Pull data from Python every 1 second
  setInterval(async () => {
      try {
          let response = await fetch(`${BACKEND_URL}/get-chart-data`);
          let data = await response.json(); // This is the list of 80 readings
          
          // 1. Get all unique timestamps and sort them chronologically
          let timeLabels = [...new Set(data.map(row => row.timestamp))].sort();
          powerChart.data.labels = timeLabels;

          // 2. Create empty arrays for all 4 cats
          let cat1Data = new Array(timeLabels.length).fill(null);
          let cat2Data = new Array(timeLabels.length).fill(null);
          let cat3Data = new Array(timeLabels.length).fill(null);
          let cat4Data = new Array(timeLabels.length).fill(null);

          // 3. Sort the data into the correct cat's array, matching the exact timestamp
          data.forEach(row => {
              let timeIndex = timeLabels.indexOf(row.timestamp);
              if (row.cat_id === 1) cat1Data[timeIndex] = row.power_mA;
              if (row.cat_id === 2) cat2Data[timeIndex] = row.power_mA;
              if (row.cat_id === 3) cat3Data[timeIndex] = row.power_mA;
              if (row.cat_id === 4) cat4Data[timeIndex] = row.power_mA;
          });

          // 4. Update the graph datasets
          powerChart.data.datasets[0].data = cat1Data;
          powerChart.data.datasets[1].data = cat2Data;
          powerChart.data.datasets[2].data = cat3Data;
          powerChart.data.datasets[3].data = cat4Data;
          
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