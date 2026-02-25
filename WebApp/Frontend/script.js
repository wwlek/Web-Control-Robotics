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
  const level = battery.dataset.level;
  battery.querySelector('.battery-fill').style.width = level + '%';
});