// @ts-check
/*
 * The behaviour of a layout: sidebar toggles, drawers, remembered state.
 *
 * Load it in the head, without defer. Each layout mounts itself from a script
 * right after its markup, so its sidebars and toggles are settled before the
 * first paint. Layouts added later (htmx, a modal's content) mount the same
 * way, and a MutationObserver catches any that arrive without running scripts.
 *
 * Whether a sidebar is beside the page or a drawer over it is decided by the
 * stylesheet, from the layout's own width (container queries). The script
 * reads that decision from the sidebar's --mvpl-mode and never makes it.
 */

/**
 * @typedef {"left" | "right"} Side
 *   The reading-start and reading-end side. Under dir="rtl" "left" is drawn at
 *   the right.
 *
 * @typedef {object} PresentSidebar
 * @property {true} present
 * @property {string} mode "docked" or "overlay" (a drawer), as the stylesheet decides.
 * @property {string | null} state "open" or "closed", the docked state.
 * @property {string | null} collapse What closing leaves: "none", "icons" or "hide".
 * @property {boolean} rail Whether the sidebar is closed to its icon rail.
 * @property {boolean} visible Whether the sidebar is showing, docked or as a drawer.
 *
 * @typedef {{ present: false }} AbsentSidebar
 * @typedef {PresentSidebar | AbsentSidebar} SidebarState
 * @typedef {{ left: SidebarState, right: SidebarState }} LayoutState
 * @typedef {CustomEvent<LayoutState>} LayoutChangeEvent The "mvpl:change" event.
 * @typedef {HTMLElement | string} LayoutRef A layout's element or its id.
 */
(function () {
  "use strict";
  var host = /** @type {Window & { MvpLayout?: typeof MvpLayout }} */ (window);
  if (host.MvpLayout) return;

  var ROOT = "[data-mvpl]";
  var FOCUSABLE =
    'a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
  /** @type {WeakMap<HTMLElement, ResizeObserver>} */
  var observers = new WeakMap();
  /** @type {WeakMap<HTMLElement, HTMLElement | null>} */
  var openers = new WeakMap();
  /** @type {HTMLElement[]} */
  var stack = [];

  /**
   * @param {HTMLElement} root
   * @returns {HTMLElement | null}
   */
  function grid(root) {
    return root.querySelector(":scope > .mvpl-grid");
  }
  // A sidebar with an empty panel isn't there: it takes no space and has no toggles.
  var PRESENT = ".mvpl-sidebar:not(:has(> .mvpl-panel:empty))";
  /**
   * @param {HTMLElement} root
   * @returns {HTMLElement[]}
   */
  function sidebars(root) {
    var g = grid(root);
    return g ? Array.prototype.slice.call(g.querySelectorAll(":scope > " + PRESENT)) : [];
  }
  /**
   * @param {HTMLElement} root
   * @param {string | null} side
   * @returns {HTMLElement | null}
   */
  function sidebar(root, side) {
    var g = grid(root);
    return g ? g.querySelector(":scope > " + PRESENT + '[data-mvpl-side="' + side + '"]') : null;
  }
  /**
   * @param {HTMLElement} sb
   * @returns {HTMLElement}
   */
  function panel(sb) {
    return /** @type {HTMLElement} */ (sb.querySelector(":scope > .mvpl-panel"));
  }
  /**
   * @param {Element} el
   * @returns {HTMLElement | null}
   */
  function ownRoot(el) {
    var id = el.getAttribute("data-mvpl-layout");
    return id ? document.getElementById(id) : el.closest(ROOT);
  }
  /** @param {HTMLElement} sb */
  function mode(sb) {
    return getComputedStyle(sb).getPropertyValue("--mvpl-mode").trim() || "docked";
  }
  /** @param {HTMLElement | null} sb */
  function isVisible(sb) {
    if (!sb) return false;
    if (mode(sb) === "overlay") return sb.getAttribute("data-mvpl-overlay") === "open";
    return sb.getAttribute("data-mvpl-state") === "open" || sb.getAttribute("data-mvpl-collapse") === "none";
  }
  /** @param {HTMLElement | null} sb */
  function canToggle(sb) {
    return !!sb && !(mode(sb) === "docked" && sb.getAttribute("data-mvpl-collapse") === "none");
  }

  /**
   * @param {HTMLElement} root
   * @returns {LayoutState}
   */
  function state(root) {
    var out = /** @type {LayoutState} */ ({});
    /** @type {Side[]} */ (["left", "right"]).forEach(function (side) {
      var sb = sidebar(root, side);
      out[side] = sb
        ? {
            present: true,
            mode: mode(sb),
            state: sb.getAttribute("data-mvpl-state"),
            collapse: sb.getAttribute("data-mvpl-collapse"),
            rail: sb.hasAttribute("data-mvpl-rail"),
            visible: isVisible(sb),
          }
        : { present: false };
    });
    return out;
  }

  // Everything a toggle, or an element shown only in one state, needs to know
  // about its own layout, and nothing about a layout nested inside it.
  /** @param {HTMLElement} root */
  function controls(root) {
    return Array.prototype.slice
      .call(document.querySelectorAll("[data-mvpl-toggle], [data-mvpl-when]"))
      .filter(function (el) {
        return ownRoot(el) === root;
      });
  }

  /** @param {HTMLElement} root */
  function measure(root) {
    var g = grid(root);
    if (!g) return;
    /** @type {HTMLElement | null} */
    var header = g.querySelector(":scope > .mvpl-header");
    /** @type {HTMLElement | null} */
    var footer = g.querySelector(":scope > .mvpl-footer");
    root.style.setProperty("--mvpl-header-h", (header ? header.offsetHeight : 0) + "px");
    root.style.setProperty("--mvpl-footer-h", (footer ? footer.offsetHeight : 0) + "px");
  }

  function lockPage() {
    var locked = !!document.querySelector(
      '.mvpl:not([data-mvpl-container]) > .mvpl-grid > .mvpl-sidebar[data-mvpl-overlay="open"]'
    );
    document.documentElement.classList.toggle("mvpl-locked", locked);
    document.documentElement.style.overflow = locked ? "hidden" : "";
  }

  /** @param {HTMLElement | null} root */
  function sync(root) {
    if (!root || !root.isConnected) return;
    sidebars(root).forEach(function (sb) {
      var now = mode(sb);
      var before = sb.getAttribute("data-mvpl-mode");
      if (before && before !== now && sb.getAttribute("data-mvpl-overlay") === "open") {
        closeOverlay(sb, false);
      }
      sb.setAttribute("data-mvpl-mode", now);
      sb.toggleAttribute(
        "data-mvpl-rail",
        now === "docked" && sb.getAttribute("data-mvpl-state") === "closed" && sb.getAttribute("data-mvpl-collapse") === "icons"
      );
    });
    controls(root).forEach(function (el) {
      if (el.hasAttribute("data-mvpl-toggle")) {
        var sb = sidebar(root, el.getAttribute("data-mvpl-toggle"));
        var when = el.getAttribute("data-mvpl-when");
        var show = canToggle(sb);
        if (show && when === "closed") show = !isVisible(sb);
        if (show && when === "open") show = isVisible(sb);
        el.hidden = !show;
        if (sb) {
          el.setAttribute("aria-controls", sb.id);
          el.setAttribute("aria-expanded", String(isVisible(sb)));
        }
      } else {
        var parts = (el.getAttribute("data-mvpl-when") || "").split("-");
        var target = sidebar(root, parts[0]);
        var visible = isVisible(target);
        el.hidden = !(target && (parts[1] === "closed" ? !visible : visible));
      }
    });
    measure(root);
    lockPage();
    root.dispatchEvent(new CustomEvent("mvpl:change", { bubbles: true, detail: state(root) }));
  }

  /**
   * @param {HTMLElement} sb
   * @param {HTMLElement | null} opener
   */
  function openOverlay(sb, opener) {
    var root = /** @type {HTMLElement} */ (ownRoot(sb));
    var p = panel(sb);
    sb.setAttribute("data-mvpl-overlay", "open");
    openers.set(sb, opener || /** @type {HTMLElement | null} */ (document.activeElement));
    // What the backdrop covers can't be reached while the drawer is open.
    Array.prototype.forEach.call(/** @type {HTMLElement} */ (grid(root)).children, function (child) {
      if (child !== sb && !child.inert) {
        child.inert = true;
        child.setAttribute("data-mvpl-inerted", "");
      }
    });
    p.setAttribute("role", "dialog");
    p.setAttribute("aria-modal", "true");
    var label = sb.getAttribute("aria-label");
    if (label) p.setAttribute("aria-label", label);
    if (!p.hasAttribute("tabindex")) p.setAttribute("tabindex", "-1");
    stack.push(sb);
    (reachable(p)[0] || p).focus({ preventScroll: true });
  }

  /**
   * @param {HTMLElement} sb
   * @param {boolean} returnFocus
   */
  function closeOverlay(sb, returnFocus) {
    if (sb.getAttribute("data-mvpl-overlay") !== "open") return;
    var root = ownRoot(sb);
    var p = panel(sb);
    sb.removeAttribute("data-mvpl-overlay");
    if (root) {
      Array.prototype.forEach.call(/** @type {HTMLElement} */ (grid(root)).querySelectorAll(":scope > [data-mvpl-inerted]"), function (child) {
        child.inert = false;
        child.removeAttribute("data-mvpl-inerted");
      });
    }
    p.removeAttribute("role");
    p.removeAttribute("aria-modal");
    stack = stack.filter(function (other) {
      return other !== sb;
    });
    var opener = openers.get(sb);
    openers.delete(sb);
    if (returnFocus && opener && opener.isConnected) {
      // A toggle that shows only while its sidebar is out of sight is still
      // hidden here, and a hidden element takes no focus: show it first.
      if (root) sync(root);
      opener.focus({ preventScroll: true });
    }
  }

  /** @param {HTMLElement} sb */
  function remember(sb) {
    var name = sb.getAttribute("data-mvpl-persist");
    if (!name) return;
    document.cookie =
      "mvpl-" + name + "=" + sb.getAttribute("data-mvpl-state") + "; path=/; max-age=31536000; samesite=lax";
  }

  /**
   * @param {HTMLElement} root
   * @param {string | null} side
   * @param {HTMLElement | null} opener
   */
  function toggle(root, side, opener) {
    var sb = sidebar(root, side);
    if (!sb || !canToggle(sb)) return;
    if (mode(sb) === "overlay") {
      if (sb.getAttribute("data-mvpl-overlay") === "open") closeOverlay(sb, true);
      else openOverlay(sb, opener);
    } else {
      sb.setAttribute("data-mvpl-state", sb.getAttribute("data-mvpl-state") === "open" ? "closed" : "open");
      remember(sb);
    }
    sync(root);
  }

  /**
   * @param {LayoutRef} rootOrId
   * @returns {HTMLElement}
   */
  function resolve(rootOrId) {
    var root = typeof rootOrId === "string" ? document.getElementById(rootOrId) : rootOrId;
    if (!root || !root.matches(ROOT)) {
      throw new Error(
        typeof rootOrId === "string"
          ? "MvpLayout: no layout has the id " + JSON.stringify(rootOrId)
          : "MvpLayout: the element is not a layout"
      );
    }
    return root;
  }

  /**
   * @param {ParentNode} scope
   * @returns {NodeListOf<HTMLElement>}
   */
  function layouts(scope) {
    return scope.querySelectorAll(ROOT);
  }

  var uid = 0;
  /** @param {HTMLElement | null} root */
  function mount(root) {
    if (!root) return;
    // A toggle names the sidebar it controls, which needs an id.
    sidebars(root).forEach(function (sb) {
      if (!sb.id) sb.id = "mvpl-sidebar-" + ++uid;
    });
    if (!observers.has(root)) {
      var observer = new ResizeObserver(function () {
        sync(root);
      });
      observer.observe(root);
      var g = grid(root);
      if (g) {
        Array.prototype.forEach.call(g.querySelectorAll(":scope > .mvpl-header, :scope > .mvpl-footer"), function (el) {
          observer.observe(el);
        });
      }
      observers.set(root, observer);
    }
    sync(root);
  }

  document.addEventListener("click", function (event) {
    var target = event.target instanceof Element ? event.target : null;
    if (!target) return;
    /** @type {HTMLElement | null} */
    var button = target.closest("[data-mvpl-toggle]");
    if (button) {
      var root = ownRoot(button);
      if (root) toggle(root, button.getAttribute("data-mvpl-toggle"), button);
      return;
    }
    var closer = target.closest("[data-mvpl-close]");
    if (closer) {
      /** @type {HTMLElement | null} */
      var sb = closer.closest(".mvpl-sidebar");
      if (sb) {
        closeOverlay(sb, true);
        sync(ownRoot(sb));
      }
      return;
    }
    // Following a link from a drawer closes it, as leaving the page would.
    var link = target.closest("a[href]");
    /** @type {HTMLElement | null} */
    var drawer = link && link.closest('.mvpl-sidebar[data-mvpl-overlay="open"]');
    if (drawer && !event.defaultPrevented) {
      closeOverlay(drawer, false);
      sync(ownRoot(drawer));
    }
  });

  /** @param {HTMLElement} p */
  function reachable(p) {
    return Array.prototype.filter.call(p.querySelectorAll(FOCUSABLE), function (el) {
      return el.checkVisibility ? el.checkVisibility() : true;
    });
  }

  document.addEventListener("keydown", function (event) {
    if (!stack.length) return;
    var sb = stack[stack.length - 1];
    if (event.key === "Tab") {
      // Only a whole-page drawer is modal to the browser's own tab order; a
      // contained one is trapped here, so focus stays in whichever is topmost.
      var p = panel(sb);
      var items = reachable(p);
      var first = items[0] || p;
      var last = items[items.length - 1] || p;
      var active = document.activeElement;
      if (!p.contains(active) || (event.shiftKey && (active === first || active === p))) {
        event.preventDefault();
        (event.shiftKey ? last : first).focus({ preventScroll: true });
      } else if (!event.shiftKey && active === last) {
        event.preventDefault();
        first.focus({ preventScroll: true });
      }
      return;
    }
    if (event.key !== "Escape") return;
    closeOverlay(sb, true);
    sync(ownRoot(sb));
    // Escape closes the drawer and nothing else, such as a dialog around it.
    event.preventDefault();
    event.stopPropagation();
  });

  // The header of a layout that has been scrolled gets a line under it.
  document.addEventListener(
    "scroll",
    function (event) {
      var target = event.target;
      if (target === document) {
        document.querySelectorAll(".mvpl:not([data-mvpl-container])").forEach(function (root) {
          root.toggleAttribute("data-mvpl-scrolled", window.scrollY > 0);
        });
      } else if (target instanceof Element && target.matches(".mvpl[data-mvpl-container] > .mvpl-grid")) {
        /** @type {HTMLElement} */ (target.parentElement).toggleAttribute("data-mvpl-scrolled", target.scrollTop > 0);
      }
    },
    { capture: true, passive: true }
  );

  new MutationObserver(function (records) {
    records.forEach(function (record) {
      record.addedNodes.forEach(function (node) {
        if (!(node instanceof Element)) return;
        if (node.matches(ROOT)) mount(/** @type {HTMLElement} */ (node));
        layouts(node).forEach(mount);
        // A control outside its layout, such as a dock after the shell.
        /** @type {Element[]} */
        var outside = node.matches("[data-mvpl-layout]") ? [node] : [];
        node.querySelectorAll("[data-mvpl-layout]").forEach(function (el) {
          outside.push(el);
        });
        outside.forEach(function (el) {
          var root = ownRoot(el);
          if (root && observers.has(root)) sync(root);
        });
      });
    });
    stack = stack.filter(function (sb) {
      return sb.isConnected;
    });
    lockPage();
  }).observe(document.documentElement, { childList: true, subtree: true });

  // Layouts written without the mount script after them, as plain templates may be.
  function mountAll() {
    layouts(document).forEach(mount);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mountAll);
  else mountAll();

  // MvpLayout("app") mounts the layout with that id, or the element given, and
  // returns it. The rest of the API hangs off the same function. Every call
  // takes a layout's id or its element.
  /** @returns {HTMLElement | null} */
  function active() {
    return /** @type {HTMLElement | null} */ (document.activeElement);
  }

  /**
   * Mount a layout and return its element.
   * @param {LayoutRef} rootOrId
   * @returns {HTMLElement}
   * @throws {Error} When no layout has that id.
   */
  function MvpLayout(rootOrId) {
    var root = resolve(rootOrId);
    mount(root);
    return root;
  }
  /** @param {LayoutRef} rootOrId */
  MvpLayout.sync = function (rootOrId) {
    sync(resolve(rootOrId));
  };
  /**
   * @param {LayoutRef} rootOrId
   * @returns {LayoutState}
   */
  MvpLayout.state = function (rootOrId) {
    return state(resolve(rootOrId));
  };
  /**
   * @param {LayoutRef} rootOrId
   * @param {Side} side
   */
  MvpLayout.toggle = function (rootOrId, side) {
    toggle(resolve(rootOrId), side, active());
  };
  // Show a sidebar, whatever its mode: opens the drawer, or the docked sidebar.
  /**
   * @param {LayoutRef} rootOrId
   * @param {Side} side
   */
  MvpLayout.open = function (rootOrId, side) {
    var root = resolve(rootOrId);
    if (!isVisible(sidebar(root, side))) toggle(root, side, active());
  };
  /**
   * @param {LayoutRef} rootOrId
   * @param {Side} side
   */
  MvpLayout.close = function (rootOrId, side) {
    var root = resolve(rootOrId);
    var sb = sidebar(root, side);
    if (isVisible(sb) && canToggle(sb)) toggle(root, side, active());
  };
  host.MvpLayout = MvpLayout;
})();
