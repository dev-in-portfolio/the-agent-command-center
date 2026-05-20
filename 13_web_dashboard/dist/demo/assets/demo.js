(() => {
  const breadcrumbLabels = {
    "/demo": "Demo Hub",
    "/demo/": "Demo Hub",
    "/demo/index.html": "Demo Hub",
    "/demo/simulator.html": "Simulator",
    "/demo/system-story.html": "System Story",
    "/demo/system-scale.html": "System Scale",
    "/demo/agent-hierarchy.html": "Agent / Department Hierarchy",
    "/demo/agent-registry.html": "Agent Registry",
    "/demo/operating-model.html": "Operating Model",
    "/demo/validator-safety-map.html": "Validator & Safety Gate Map",
    "/demo/safety-boundaries.html": "Safety Boundaries",
    "/demo/technical-appendix.html": "Technical Appendix",
    "/demo/objections.html": "Objections / FAQ",
    "/demo/review.html": "Review / Scorecard",
    "/demo/review-qa.html": "Review QA Checklist",
    "/demo/presentation.html": "Presentation",
  };

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
  const currentLabel = breadcrumbLabels[current] || breadcrumbLabels[`${current}/`] || "Demo Hub";

  if (document.querySelector(".demo-shell") && !document.querySelector(".breadcrumb")) {
    const topbar = document.querySelector(".topbar");
    if (topbar && topbar.parentElement) {
      const breadcrumb = document.createElement("p");
      breadcrumb.className = "breadcrumb";
      breadcrumb.innerHTML = '<a href="../index.html">Home</a><span aria-hidden="true">→</span><a href="./index.html">Demo Hub</a><span aria-hidden="true">→</span><span>' + currentLabel + "</span>";
      topbar.insertAdjacentElement("afterend", breadcrumb);
    }
  }

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
