// Potwierdzenia i zaznaczanie linku bez skryptów inline (CSP: script-src 'self').
document.addEventListener("submit", e => {
  const msg = e.target.dataset.confirm;
  if (msg && !confirm(msg)) e.preventDefault();
});
document.addEventListener("focusin", e => {
  if ("select" in e.target.dataset) e.target.select();
});
