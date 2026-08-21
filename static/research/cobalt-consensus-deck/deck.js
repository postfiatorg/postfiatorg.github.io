(() => {
  const scroller = document.getElementById("slides");
  const slides = [...document.querySelectorAll(".slide")];
  const dotsRoot = document.getElementById("deckDots");
  const current = document.getElementById("currentSlide");
  const fill = document.getElementById("progressFill");
  const prev = document.getElementById("prevSlide");
  const next = document.getElementById("nextSlide");
  const dialog = document.getElementById("sourceDialog");
  const openers = [
    document.getElementById("sourcesButton"),
    document.getElementById("sourceQuick"),
  ].filter(Boolean);
  const close = document.getElementById("sourceClose");
  const reduced = matchMedia("(prefers-reduced-motion: reduce)");
  let active = 0;

  if (!scroller || !slides.length) return;

  const dots = slides.map((slide, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.setAttribute(
      "aria-label",
      `Go to slide ${index + 1}: ${slide.querySelector("h1,h2")?.textContent.trim() || ""}`,
    );
    button.addEventListener("click", () => go(index));
    dotsRoot.append(button);
    return button;
  });

  function setActive(index, updateHash = false) {
    active = Math.max(0, Math.min(slides.length - 1, index));
    slides.forEach((slide, i) => {
      slide.classList.toggle("is-active", i === active);
      slide.setAttribute("aria-current", i === active ? "step" : "false");
    });
    dots.forEach((dot, i) => {
      dot.classList.toggle("is-active", i === active);
      dot.setAttribute("aria-current", i === active ? "step" : "false");
    });
    current.textContent = String(active + 1).padStart(2, "0");
    fill.style.width = `${((active + 1) / slides.length) * 100}%`;
    prev.disabled = active === 0;
    next.disabled = active === slides.length - 1;
    if (updateHash) history.replaceState(null, "", `#slide-${active + 1}`);
  }

  function go(index, focus = false) {
    const target = Math.max(0, Math.min(slides.length - 1, index));
    slides[target].scrollIntoView({
      behavior: reduced.matches ? "auto" : "smooth",
      block: "start",
    });
    setActive(target, true);
    if (focus)
      setTimeout(
        () => slides[target].focus({ preventScroll: true }),
        reduced.matches ? 0 : 350,
      );
  }

  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (visible) setActive(slides.indexOf(visible.target), true);
    },
    { root: scroller, threshold: [0.5, 0.72] },
  );
  slides.forEach((slide) => observer.observe(slide));

  prev.addEventListener("click", () => go(active - 1, true));
  next.addEventListener("click", () => go(active + 1, true));
  openers.forEach((button) =>
    button.addEventListener("click", () => dialog.showModal()),
  );
  close.addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });

  document.addEventListener("keydown", (event) => {
    if (dialog.open && event.key !== "Escape") return;
    if (event.target.closest('a,button,[tabindex="0"]')) return;
    if (["ArrowDown", "ArrowRight", "PageDown", " "].includes(event.key)) {
      event.preventDefault();
      go(active + 1, true);
    }
    if (["ArrowUp", "ArrowLeft", "PageUp"].includes(event.key)) {
      event.preventDefault();
      go(active - 1, true);
    }
    if (event.key === "Home") {
      event.preventDefault();
      go(0, true);
    }
    if (event.key === "End") {
      event.preventDefault();
      go(slides.length - 1, true);
    }
  });

  const hash = location.hash.match(/^#slide-(\d{1,2})$/);
  const initial = hash
    ? Math.max(0, Math.min(slides.length - 1, Number(hash[1]) - 1))
    : 0;
  setActive(initial);
  if (initial) requestAnimationFrame(() => go(initial));
})();
