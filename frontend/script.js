const API_BASE_URL = "http://192.168.1.10:8000";

// --- Helper function for battery display ---
function updateBattery(card, level) {
  const fill = card.querySelector('.battery-fill');
  const text = card.querySelector('.battery-text');
  fill.style.width = level + '%';
  text.textContent = level + '%';
  fill.classList.remove('green','yellow','red');
  if (level > 60) fill.classList.add('green');
  else if (level > 30) fill.classList.add('yellow');
  else fill.classList.add('red');
}

// 1. CAT CONTROL LOGIC
document.querySelectorAll('.card').forEach(card => {
  const stopBtn = card.querySelector('.toggle.stop');
  const danceBtn = card.querySelector('.toggle.dance');
  const catId = card.dataset.cat;

  // Stop button
  stopBtn?.addEventListener('click', async () => {
    const isActive = stopBtn.classList.toggle('active');
    card.classList.toggle('disabled', isActive);
    if (isActive) danceBtn?.classList.remove('active');

    if (!catId || card.classList.contains('disabled')) return;

    try {
      const res = await fetch(`${API_BASE_URL}/stop`, {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cat: catId })
      });
      if (!res.ok) throw new Error(`Stop failed for cat ${catId}`);
      console.log(`Stop sent for cat ${catId}`);
    } catch(err) { console.error(err); }
  });

  // Dance button
  danceBtn?.addEventListener('click', async () => {
    if (card.classList.contains('disabled')) return;
    danceBtn.classList.toggle('active');

    if (!catId) return;
    try {
      const res = await fetch(`${API_BASE_URL}/dance`, {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cat: catId })
      });
      if (!res.ok) throw new Error(`Dance failed for cat ${catId}`);
      console.log(`Dance sent for cat ${catId}`);
    } catch(err) { console.error(err); }
  });

  // Direction buttons
  card.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      if (card.classList.contains('disabled')) return;
      const dir = btn.dataset.action;
      const direction = dir === "up" ? "forward" :
                        dir === "left" ? "left" :
                        dir === "right" ? "right" : null;
      if (!direction || !catId) return;

      try {
        const res = await fetch(`${API_BASE_URL}/move`, {
          method: "POST",
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ cat: catId, direction })
        });
        if (!res.ok) throw new Error(`Move failed for cat ${catId}`);
        console.log(`Move sent for cat ${catId}: ${direction}`);
      } catch(err) { console.error(err); }
    });
  });
});

// Global stop
document.getElementById('all-stop')?.addEventListener('click', async () => {
  document.querySelectorAll('.card:not(.global-control)').forEach(card => {
    card.classList.add('disabled');
    card.querySelector('.toggle.stop')?.classList.add('active');
    card.querySelector('.toggle.dance')?.classList.remove('active');
  });

  try {
    const res = await fetch(`${API_BASE_URL}/stop`, {
      method: "POST",
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cat: "all" })
    });
    if (!res.ok) throw new Error("Global stop failed");
    console.log("Global stop sent");
  } catch(err) { console.error(err); }
});

// Global dance
document.getElementById('all-dance')?.addEventListener('click', async () => {
  document.querySelectorAll('.card:not(.global-control)').forEach(card => {
    if (card.classList.contains('disabled')) return;
    card.querySelector('.toggle.dance')?.classList.add('active');
  });

  try {
    const res = await fetch(`${API_BASE_URL}/dance`, {
      method: "POST",
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cat: "all" })
    });
    if (!res.ok) throw new Error("Global dance failed");
    console.log("Global dance sent");
  } catch(err) { console.error(err); }
});

// 2. BATTERY INIT
document.querySelectorAll('.battery').forEach(battery => {
  const card = battery.closest('.card');
  const level = Number(battery.dataset.level);
  updateBattery(card, level);
});

// 3. CHARTS
const catCharts = {};
const chartColors = { 1:'#ef4444',2:'#facc15',3:'#22c55e',4:'#3b82f6' };
const LOW_VOLTAGE_THRESHOLD = 7.2;

// Initialize charts
[1,2,3,4].forEach(id => {
  const canvas = document.getElementById(`chart-cat-${id}`);
  if (!canvas) return;
  catCharts[id] = new Chart(canvas.getContext('2d'), {
    type: 'line',
    data: { labels:[1,2,3,4,5], datasets:[{
      data:[0,0,0,0,0],
      borderColor: chartColors[id],
      backgroundColor: chartColors[id]+'22',
      borderWidth:2,
      fill:true,
      tension:0.35,
      pointRadius:0
    }]},
    options: {
      responsive:true,
      maintainAspectRatio:false,
      animation:false,
      plugins:{legend:{display:false}},
      scales:{x:{display:false}, y:{beginAtZero:false,ticks:{maxTicksLimit:4}}}
    }
  });
});

// 4. POLLING CAT STATUS
async function pollStatus() {
  try {
    const res = await fetch(`${API_BASE_URL}/status`);
    if (!res.ok) throw new Error("Failed to fetch status");
    const data = await res.json(); // { "1": {voltage:[...], battery:...}, ... }

    Object.entries(data).forEach(([catId, status]) => {
      const id = Number(catId);
      const values = status.voltage || [0,0,0,0,0];
      const batteryLevel = status.battery ?? 100;

      // ----- Chart update -----
      const chart = catCharts[id];
      if (chart) {
        chart.data.datasets[0].data = values;
        const latest = values[values.length-1] ?? 0;
        const isLow = latest < LOW_VOLTAGE_THRESHOLD;
        chart.data.datasets[0].borderColor = isLow ? '#ef4444' : chartColors[id];
        chart.data.datasets[0].backgroundColor = (isLow ? '#ef4444' : chartColors[id])+'22';
        smoothScale(chart, values);
        chart.update('none');
      }

      // ----- Battery update -----
      const card = document.querySelector(`.card[data-cat="${id}"]`);
      if (card) updateBattery(card, batteryLevel);
    });

  } catch(err) {
    console.error("Error polling status:", err);
  } finally {
    setTimeout(pollStatus, 1000); // Poll every second
  }
}

// Smooth Y scale helper
function smoothScale(chart, values) {
  const min = Math.min(...values), max = Math.max(...values), padding=0.1;
  const targetMin = min-padding, targetMax = max+padding;
  const currentMin = chart.options.scales.y.min ?? targetMin;
  const currentMax = chart.options.scales.y.max ?? targetMax;
  chart.options.scales.y.min = currentMin + (targetMin-currentMin)*0.2;
  chart.options.scales.y.max = currentMax + (targetMax-currentMax)*0.2;
}

// Start polling
pollStatus();