// Entering a temple card replays its ivy (class rg); the class stays, so leaving replays nothing.
document.querySelectorAll<HTMLElement>('.tcard').forEach((card) => {
  card.addEventListener('mouseenter', () => {
    card.classList.remove('rg');
    void card.offsetWidth; // reflow, so the animations restart
    card.classList.add('rg');
  });
});
