(() => {
  const deck = document.querySelector(".arcdeck");
  if (!deck) return;
  deck.classList.add("js");
  const slides = [...deck.querySelectorAll(".slide")];
  const layers = [...deck.querySelectorAll(".arcdeck__layer")];
  const current = deck.querySelector("#arcdeckCurrent");
  const fill = deck.querySelector("#arcdeckFill");
  const prev = deck.querySelector("#arcdeckPrev");
  const next = deck.querySelector("#arcdeckNext");
  let active = 0;
  let deckVisible = false;

  function setWorld(name) {
    layers.forEach((l) => l.classList.toggle("is-active", l.dataset.world === name));
  }
  function setActive(i) {
    active = Math.max(0, Math.min(slides.length - 1, i));
    slides.forEach((s, k) => s.classList.toggle("is-active", k === active));
    setWorld(slides[active].dataset.world);
    if (current) current.textContent = String(active + 1).padStart(2, "0");
    if (fill) fill.style.width = `${((active + 1) / slides.length) * 100}%`;
    if (prev) prev.disabled = active === 0;
    if (next) next.disabled = active === slides.length - 1;
  }
  function goTo(i) {
    const target = slides[Math.max(0, Math.min(slides.length - 1, i))];
    target.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" });
  }

  const io = new IntersectionObserver((entries) => {
    let best = null;
    entries.forEach((e) => { if (e.isIntersecting && (!best || e.intersectionRatio > best.intersectionRatio)) best = e; });
    if (best) setActive(slides.indexOf(best.target));
  }, { threshold: [0.5, 0.75] });
  slides.forEach((s) => io.observe(s));

  new IntersectionObserver((entries) => { deckVisible = entries[0].isIntersecting; }, { threshold: 0.01 }).observe(deck);

  prev?.addEventListener("click", () => goTo(active - 1));
  next?.addEventListener("click", () => goTo(active + 1));
  document.addEventListener("keydown", (e) => {
    if (!deckVisible || e.altKey || e.ctrlKey || e.metaKey) return;
    const tag = document.activeElement?.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA") return;
    if (e.key === "ArrowRight" || e.key === "PageDown") { e.preventDefault(); goTo(active + 1); }
    if (e.key === "ArrowLeft" || e.key === "PageUp") { e.preventDefault(); goTo(active - 1); }
  });

  setActive(0);
})();
