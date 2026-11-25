// Auto-open MkDocs Material search when navigated to /docs/l1/?q=...
(function () {
  function applyQueryParam() {
    var params = new URLSearchParams(window.location.search);
    var q = (params.get("q") || "").trim();
    if (!q) return;
    var toggle = document.querySelector("[data-md-toggle='search']");
    var input = document.querySelector(".md-search__input");
    if (!input) return;
    if (toggle) toggle.checked = true;
    input.focus();
    input.value = q;
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new KeyboardEvent("keyup", { bubbles: true, key: "Enter" }));
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      setTimeout(applyQueryParam, 250);
    });
  } else {
    setTimeout(applyQueryParam, 250);
  }
})();
