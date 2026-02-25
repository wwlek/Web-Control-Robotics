const API_BASE_URL = "http://127.0.0.1:5500/backend/main.py";
// anpassen, falls Backend woanders läuft

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

// Akkuanzeige initialisieren
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


document.getElementById('all-stop')?.addEventListener('click', () => {
  document.querySelectorAll('.card:not(.global-control)').forEach(card => {
    card.classList.add('disabled');
    card.querySelector('.toggle.stop')?.classList.add('active');
    card.querySelector('.toggle.dance')?.classList.remove('active');
  });
});

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

  danceBtn.addEventListener('click', async () => {
    if (card.classList.contains('disabled')) return;

    danceBtn.classList.toggle('active');

    try {
      const res = await fetch(`${API_BASE_URL}/trigger-dance`, {
        method: "POST"
      });

      if (!res.ok) {
        throw new Error("Dance command failed");
      }

      console.log("Dance command sent successfully");
    } catch (err) {
      console.error("Error triggering dance:", err);
      danceBtn.classList.remove('active');
    }
  });
});