// ─── LIVE TICKER ANIMATION ──────────────────────────────────────────────────
function initTicker() {
  const ticker = document.getElementById('ticker');
  if (!ticker) return;

  // Clone items for seamless loop
  const items = ticker.innerHTML;
  ticker.innerHTML += items;
}

// Initialize on load
window.addEventListener('load', () => {
  initTicker();
  console.log("EcoValue India Frontend Loaded");
});