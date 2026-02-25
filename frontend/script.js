const API_BASE_URL = "http://192.168.1.10:8000";

document.querySelectorAll('.card').forEach(card => {
  const stopBtn = card.querySelector('.toggle.stop');
  const danceBtn = card.querySelector('.toggle.dance');

  stopBtn.addEventListener('click', () => {
    const isActive = stopBtn.classList.toggle('active');
    card.classList.toggle('disabled', isActive);

    if (isActive) {
      danceBtn.classList.remove('active');
    }
  });

  danceBtn.addEventListener('click', () => {
    if (card.classList.contains('disabled')) return;
    danceBtn.classList.toggle('active');
  });
});

// Initialize battery levels
document.querySelectorAll('.battery').forEach(battery => {
  const level = Number(battery.dataset.level);
  const fill = battery.querySelector('.battery-fill');
  const text = battery.querySelector('.battery-text');

  fill.style.width = level + '%';
  text.textContent = level + '%';

  fill.classList.remove('green', 'yellow', 'red');

  if (level > 60) {
    fill.classList.add('green');
  } else if (level > 30) {
    fill.classList.add('yellow');
  } else {
    fill.classList.add('red');
  }
});

// Handle global stop (for all cats)
document.getElementById('all-stop')?.addEventListener('click', async () => {
  document.querySelectorAll('.card:not(.global-control)').forEach(card => {
    card.classList.add('disabled');
    card.querySelector('.toggle.stop')?.classList.add('active');
    card.querySelector('.toggle.dance')?.classList.remove('active');
  });

  try {
    const res = await fetch(`${API_BASE_URL}/stop`, {
      method: "POST",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ cat: "all" })
    });

    if (!res.ok) {
      throw new Error("Global stop failed");
    }

    console.log("Global stop command sent successfully");
  } catch (err) {
    console.error("Error triggering global stop:", err);
  }
});

// Handle global dance (for all cats)
document.getElementById('all-dance')?.addEventListener('click', async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/dance`, {
      method: "POST",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ cat: "all" })
    });

    if (!res.ok) {
      throw new Error("Global dance failed");
    }

    console.log("Global dance command sent successfully");
  } catch (err) {
    console.error("Error triggering global dance:", err);
  }
});

// Handle individual cat controls (move)
document.querySelectorAll('.card').forEach(card => {
  const stopBtn = card.querySelector('.toggle.stop');
  const danceBtn = card.querySelector('.toggle.dance');
  const catId = card.dataset.cat; // Get the cat ID (1, 2, 3, 4)

  // Handle move button clicks
  card.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('click', async () => {
      // Prevent action if cat is disabled
      if (card.classList.contains('disabled')) return;

      const action = button.dataset.action;
      const direction = action === "up" ? "forward" :
                        action === "left" ? "left" :
                        action === "right" ? "right" : null;

      if (!direction) return;

      try {
        const res = await fetch(`${API_BASE_URL}/move`, {
          method: "POST",
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            direction: direction,
            cat: catId // Send the specific cat ID (1, 2, 3, or 4)
          })
        });

        if (!res.ok) {
          throw new Error(`Move command failed for cat ${catId}`);
        }

        console.log(`Move command sent successfully for cat ${catId}: ${direction}`);
      } catch (err) {
        console.error(`Error triggering move for cat ${catId}:`, err);
      }
    });
  });

  // Handle stop button click for individual cat
  stopBtn.addEventListener('click', async () => {
    if (card.classList.contains('disabled')) return;

    try {
      const res = await fetch(`${API_BASE_URL}/stop`, {
        method: "POST",
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ cat: catId })
      });

      if (!res.ok) {
        throw new Error(`Stop command failed for cat ${catId}`);
      }

      console.log(`Stop command sent successfully for cat ${catId}`);
    } catch (err) {
      console.error(`Error triggering stop for cat ${catId}:`, err);
    }
  });

  // Handle dance button click for individual cat
  danceBtn.addEventListener('click', async () => {
    if (card.classList.contains('disabled')) return;

    try {
      const res = await fetch(`${API_BASE_URL}/dance`, {
        method: "POST",
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ cat: catId })
      });

      if (!res.ok) {
        throw new Error(`Dance command failed for cat ${catId}`);
      }

      console.log(`Dance command sent successfully for cat ${catId}`);
    } catch (err) {
      console.error(`Error triggering dance for cat ${catId}:`, err);
    }
  });
});