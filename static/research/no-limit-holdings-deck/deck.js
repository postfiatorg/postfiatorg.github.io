(() => {
  const root = document.documentElement;
  const scroller = document.getElementById("slides");
  const slides = [...document.querySelectorAll(".slide")];
  const worlds = [...document.querySelectorAll(".world__layer")];
  const dotsRoot = document.getElementById("deckDots");
  const currentLabel = document.getElementById("currentSlide");
  const progressFill = document.getElementById("progressFill");
  const previousButton = document.getElementById("prevSlide");
  const nextButton = document.getElementById("nextSlide");
  const sourcesButton = document.getElementById("sourcesButton");
  const sourceDialog = document.getElementById("sourceDialog");
  const sourceClose = document.getElementById("sourceClose");
  const sourceGroups = [...document.querySelectorAll("[data-source-slide]")];
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  let activeIndex = 0;
  let animationFrame = 0;

  if (!scroller || slides.length === 0) return;

  const dots = slides.map((slide, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.setAttribute("aria-label", `Go to slide ${index + 1}: ${slide.querySelector("h1,h2")?.textContent.trim() || ""}`);
    button.addEventListener("click", () => goTo(index));
    dotsRoot.appendChild(button);
    return button;
  });

  function setWorld(name) {
    document.body.dataset.activeWorld = name;
    worlds.forEach((world) => {
      world.classList.toggle("is-active", world.dataset.world === name);
    });
  }

  function selectSources(index) {
    sourceGroups.forEach((group) => {
      group.hidden = Number(group.dataset.sourceSlide) !== index + 1;
    });
  }

  function setActive(index, updateHash = false) {
    activeIndex = Math.max(0, Math.min(slides.length - 1, index));
    slides.forEach((slide, slideIndex) => {
      const active = slideIndex === activeIndex;
      slide.classList.toggle("is-active", active);
      slide.setAttribute("aria-current", active ? "step" : "false");
    });
    dots.forEach((dot, dotIndex) => {
      const active = dotIndex === activeIndex;
      dot.classList.toggle("is-active", active);
      dot.setAttribute("aria-current", active ? "step" : "false");
    });

    const number = String(activeIndex + 1).padStart(2, "0");
    currentLabel.textContent = number;
    progressFill.style.width = `${((activeIndex + 1) / slides.length) * 100}%`;
    previousButton.disabled = activeIndex === 0;
    nextButton.disabled = activeIndex === slides.length - 1;
    setWorld(slides[activeIndex].dataset.world);
    selectSources(activeIndex);

    if (updateHash) {
      history.replaceState(null, "", `#slide-${activeIndex + 1}`);
    }
  }

  function goTo(index, focus = false) {
    const target = Math.max(0, Math.min(slides.length - 1, index));
    slides[target].scrollIntoView({
      behavior: reducedMotion.matches ? "auto" : "smooth",
      block: "start"
    });
    setActive(target, true);
    if (focus) {
      window.setTimeout(() => slides[target].focus({ preventScroll: true }), reducedMotion.matches ? 0 : 450);
    }
  }

  const observer = new IntersectionObserver((entries) => {
    const visible = entries
      .filter((entry) => entry.isIntersecting)
      .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (!visible) return;
    setActive(slides.indexOf(visible.target), true);
  }, {
    root: scroller,
    threshold: [0.42, 0.62, 0.82]
  });

  slides.forEach((slide) => observer.observe(slide));

  previousButton.addEventListener("click", () => goTo(activeIndex - 1, true));
  nextButton.addEventListener("click", () => goTo(activeIndex + 1, true));
  sourcesButton?.addEventListener("click", () => {
    selectSources(activeIndex);
    if (typeof sourceDialog.showModal === "function") sourceDialog.showModal();
    else sourceDialog.setAttribute("open", "");
  });
  sourceClose?.addEventListener("click", () => sourceDialog.close());
  sourceDialog?.addEventListener("click", (event) => {
    if (event.target === sourceDialog) sourceDialog.close();
  });

  document.addEventListener("keydown", (event) => {
    if (event.defaultPrevented) return;
    if (event.target.closest("details, summary, button, a, [tabindex='0']")) return;

    if (["ArrowDown", "ArrowRight", "PageDown", " "].includes(event.key)) {
      event.preventDefault();
      goTo(activeIndex + 1, true);
    }
    if (["ArrowUp", "ArrowLeft", "PageUp"].includes(event.key)) {
      event.preventDefault();
      goTo(activeIndex - 1, true);
    }
    if (event.key === "Home") {
      event.preventDefault();
      goTo(0, true);
    }
    if (event.key === "End") {
      event.preventDefault();
      goTo(slides.length - 1, true);
    }
    if (event.key === "Escape") {
      document.querySelectorAll("details[open]").forEach((detail) => detail.removeAttribute("open"));
    }
  });

  function applyLook(clientX, clientY) {
    if (reducedMotion.matches) return;
    const x = (clientX / window.innerWidth - 0.5) * 2;
    const y = (clientY / window.innerHeight - 0.5) * 2;

    cancelAnimationFrame(animationFrame);
    animationFrame = requestAnimationFrame(() => {
      root.style.setProperty("--bg-x", `${(-x * 18).toFixed(2)}px`);
      root.style.setProperty("--bg-y", `${(-y * 11).toFixed(2)}px`);
      root.style.setProperty("--fg-x", `${(x * 5).toFixed(2)}px`);
      root.style.setProperty("--fg-y", `${(y * 4).toFixed(2)}px`);
    });
  }

  window.addEventListener("pointermove", (event) => applyLook(event.clientX, event.clientY), { passive: true });
  window.addEventListener("pointerleave", () => {
    root.style.setProperty("--bg-x", "0px");
    root.style.setProperty("--bg-y", "0px");
    root.style.setProperty("--fg-x", "0px");
    root.style.setProperty("--fg-y", "0px");
  });

  reducedMotion.addEventListener?.("change", () => {
    if (reducedMotion.matches) {
      root.style.setProperty("--bg-x", "0px");
      root.style.setProperty("--bg-y", "0px");
      root.style.setProperty("--fg-x", "0px");
      root.style.setProperty("--fg-y", "0px");
    }
  });

  const hashMatch = location.hash.match(/^#slide-(\d{1,2})$/);
  const initialIndex = hashMatch ? Math.max(0, Math.min(slides.length - 1, Number(hashMatch[1]) - 1)) : 0;
  setActive(initialIndex);
  if (initialIndex > 0) {
    requestAnimationFrame(() => goTo(initialIndex));
  }
})();
