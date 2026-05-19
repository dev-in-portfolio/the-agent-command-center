(() => {
  const copyButtons = document.querySelectorAll("[data-copy-text]");
  copyButtons.forEach((button) => {
    button.addEventListener("click", async () => {
      const text = button.getAttribute("data-copy-text") || "";
      try {
        await navigator.clipboard.writeText(text);
        const original = button.textContent;
        button.textContent = "Copied";
        window.setTimeout(() => {
          button.textContent = original;
        }, 1200);
      } catch {
        button.textContent = "Copy failed";
      }
    });
  });

  document.querySelectorAll("[data-scroll-target]").forEach((button) => {
    button.addEventListener("click", () => {
      const target = document.getElementById(button.getAttribute("data-scroll-target"));
      if (target) {
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });

  document.querySelectorAll("[data-toggle-presentation]").forEach((button) => {
    button.addEventListener("click", () => {
      document.body.classList.toggle("presentation-mode");
      const active = document.body.classList.contains("presentation-mode");
      button.textContent = active ? "Exit Presentation Mode" : "Open Presentation Mode";
    });
  });

  document.querySelectorAll("[data-print-page]").forEach((button) => {
    button.addEventListener("click", () => window.print());
  });

  const current = window.location.pathname.replace(/\/+$/, "") || "/";
  document.querySelectorAll(".nav-links a").forEach((link) => {
    const href = link.getAttribute("href") || "";
    const normalized = href.replace(/\/+$/, "") || "/";
    if (
      (current === "/" && normalized === "/demo") ||
      current.endsWith(normalized) ||
      (normalized === "./" && current.endsWith("/demo")) ||
      (normalized === "../index.html" && current.endsWith("/demo"))
    ) {
      link.setAttribute("aria-current", "page");
    }
  });

  if (window.location.hash) {
    const target = document.querySelector(window.location.hash);
    if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
  }
})();
