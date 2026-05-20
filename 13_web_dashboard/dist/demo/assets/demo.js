(() => {
  const breadcrumbLabels = {
    "/demo": "Stakeholder Demo Hub",
    "/demo/": "Stakeholder Demo Hub",
    "/demo/index.html": "Stakeholder Demo Hub",
    "/demo/presentation.html": "Stakeholder Presentation",
    "/demo/simulator.html": "Command Center Sandbox Simulator",
    "/demo/system-story.html": "System Story",
    "/demo/system-scale.html": "System Scale",
    "/demo/agent-hierarchy.html": "Agent Hierarchy",
    "/demo/agent-registry.html": "Agent Registry",
    "/demo/operating-model.html": "Operating Model",
    "/demo/validator-safety-map.html": "Validator Map",
    "/demo/safety-boundaries.html": "Safety Boundaries",
    "/demo/technical-appendix.html": "Technical Appendix",
    "/demo/objections.html": "Objections",
    "/demo/review.html": "Review / Scorecard",
  };

  function copyStaticText(text, trigger) {
    if (!text) {
      return false;
    }

    const finish = (ok, message) => {
      if (!trigger) return;
      const original = trigger.textContent;
      trigger.textContent = message;
      window.setTimeout(() => {
        trigger.textContent = original;
      }, 1200);
      return ok;
    };

    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text).then(
        () => finish(true, "Copied"),
        () => fallbackCopy()
      );
    }

    return fallbackCopy();

    function fallbackCopy() {
      const textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.setAttribute("readonly", "readonly");
      textarea.style.position = "fixed";
      textarea.style.left = "-9999px";
      textarea.style.top = "0";
      document.body.appendChild(textarea);
      textarea.select();
      let ok = false;
      try {
        ok = document.execCommand("copy");
      } catch {
        ok = false;
      }
      document.body.removeChild(textarea);
      if (ok) {
        finish(true, "Copied");
        return true;
      }
      finish(false, "Copy unavailable");
      return false;
    }
  }

  function initCollapsibleMenu() {
    document.querySelectorAll("[data-collapsible-menu]").forEach((menuRoot) => {
      const toggle = menuRoot.querySelector("[data-action='toggle-menu']");
      const panel = menuRoot.querySelector("[data-menu-panel]");

      if (!toggle || !panel) return;

      const setOpen = (open) => {
        toggle.setAttribute("aria-expanded", String(open));
        toggle.setAttribute("aria-label", open ? "Close navigation menu" : "Open navigation menu");
        panel.hidden = !open;
        panel.classList.toggle("is-open", open);
        menuRoot.classList.toggle("menu-is-open", open);
      };

      setOpen(false);

      toggle.addEventListener("click", () => {
        const isOpen = toggle.getAttribute("aria-expanded") === "true";
        setOpen(!isOpen);
      });

      panel.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => setOpen(false));
      });

      document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
          setOpen(false);
        }
      });
    });
  }

  function setPresentationSlide(slideId) {
    const slides = Array.from(document.querySelectorAll(".timeline-item, [data-slide-number]"));
    if (!slides.length) return;
    slides.forEach((slide) => slide.classList.remove("active-slide"));
    const target = document.getElementById(slideId);
    if (target) {
      target.classList.add("active-slide");
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  function enterPresentationMode() {
    document.body.classList.add("presentation-mode");
  }

  function exitPresentationMode() {
    document.body.classList.remove("presentation-mode");
  }

  function initPresentationDeck() {
    document.querySelectorAll("[data-copy-text]").forEach((button) => {
      button.addEventListener("click", () => {
        copyStaticText(button.getAttribute("data-copy-text") || "", button);
      });
    });

    document.querySelectorAll("[data-scroll-target]").forEach((button) => {
      button.addEventListener("click", () => {
        const targetId = button.getAttribute("data-scroll-target");
        if (targetId) {
          setPresentationSlide(targetId);
        }
      });
    });

    document.querySelectorAll("[data-toggle-presentation]").forEach((button) => {
      button.addEventListener("click", () => {
        const active = document.body.classList.contains("presentation-mode");
        if (active) {
          exitPresentationMode();
          button.textContent = "Open Presentation Mode";
        } else {
          enterPresentationMode();
          button.textContent = "Exit Presentation Mode";
        }
      });
    });

    document.querySelectorAll("[data-print-page]").forEach((button) => {
      button.addEventListener("click", () => window.print());
    });

    if (window.location.hash) {
      const target = document.querySelector(window.location.hash);
      if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  function initDemoNavigation() {
    const current = window.location.pathname.replace(/\/+$/, "") || "/";
    const currentLabel = breadcrumbLabels[current] || breadcrumbLabels[`${current}/`] || "Stakeholder Demo Hub";

    const breadcrumb = document.querySelector(".breadcrumb");
    if (!breadcrumb && document.querySelector(".demo-shell")) {
      const topbar = document.querySelector(".demo-topbar, .topbar");
      if (topbar && topbar.parentElement) {
        const node = document.createElement("nav");
        node.className = "breadcrumb";
        node.setAttribute("aria-label", "Breadcrumb");
        node.innerHTML = '<a href="../index.html">Home</a><span aria-hidden="true">→</span><a href="./index.html">Demo Hub</a><span aria-hidden="true">→</span><span>' + currentLabel + "</span>";
        topbar.insertAdjacentElement("afterend", node);
      }
    }

    document.querySelectorAll("[data-menu-panel] a, .nav-links a").forEach((link) => {
      const href = link.getAttribute("href") || "";
      try {
        const resolved = new URL(href, window.location.href);
        const resolvedPath = resolved.pathname.replace(/\/+$/, "") || "/";
        if (resolvedPath === current) {
          link.setAttribute("aria-current", "page");
        }
      } catch {
        // Ignore malformed links in legacy pages.
      }
    });
  }

  function boot() {
    initCollapsibleMenu();
    initPresentationDeck();
    initDemoNavigation();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  window.initCollapsibleMenu = initCollapsibleMenu;
  window.initPresentationDeck = initPresentationDeck;
  window.setPresentationSlide = setPresentationSlide;
  window.enterPresentationMode = enterPresentationMode;
  window.exitPresentationMode = exitPresentationMode;
  window.copyStaticText = copyStaticText;
  window.initDemoNavigation = initDemoNavigation;
})();
