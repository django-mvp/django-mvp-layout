"""Write static/mvp_layout/layout.css.

Run with ``python scripts/build_css.py`` after changing it, and commit the result. A container query cannot
take its width from a custom property, so the drawer rules are written out once
for each breakpoint here rather than by hand.
"""

import sys
from pathlib import Path

BREAKPOINTS = {
    "sm": "40rem",
    "md": "48rem",
    "lg": "64rem",
    "xl": "80rem",
    "2xl": "96rem",
}

BASE = """\
/* Layouts arranged by a layout code, such as lHh LpR lff.
   Written by mvp_layout/build_css.py: edit that file, not this one.

   The colours are daisyUI's theme variables, so the layout follows the
   host's theme, and the system colours where daisyUI isn't installed. Every rule reaches its areas through child combinators, so a
   layout nested inside another is styled by its own code and nothing else. */

.mvpl {
  --mvpl-header-h: 0px;
  --mvpl-footer-h: 0px;
  --mvpl-dir: 1;
  --mvpl-vh: 100dvh;
  container: mvpl / inline-size;
  min-width: 0;
}
[dir="rtl"] .mvpl,
.mvpl[dir="rtl"] {
  --mvpl-dir: -1;
}

/* A contained layout fills the box it is given and scrolls inside it. Its
   root holds still, so a drawer drawn against it stays in view while the
   grid inside it scrolls. */
.mvpl[data-mvpl-container] {
  --mvpl-vh: 100cqh;
  container: mvpl / size;
  position: relative;
  overflow: hidden;
  isolation: isolate;
}

.mvpl-grid {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  grid-template-rows: auto 1fr auto;
  grid-template-areas: var(--mvpl-areas);
  min-height: 100dvh;
}
.mvpl[data-mvpl-container] > .mvpl-grid {
  height: 100%;
  min-height: 0;
  overflow: auto;
}

.mvpl-grid > .mvpl-header { grid-area: header; min-width: 0; }
.mvpl-grid > .mvpl-page { grid-area: page; min-width: 0; }
.mvpl-grid > .mvpl-footer { grid-area: footer; min-width: 0; }
.mvpl-grid > .mvpl-sidebar[data-side="left"] { grid-area: left; }
.mvpl-grid > .mvpl-sidebar[data-side="right"] { grid-area: right; }

/* Upper case in the code: the area stays in place while the layout scrolls. */
.mvpl[data-mvpl-header-fixed] > .mvpl-grid > .mvpl-header {
  position: sticky;
  top: 0;
  z-index: 30;
}
.mvpl[data-mvpl-footer-fixed] > .mvpl-grid > .mvpl-footer {
  position: sticky;
  bottom: 0;
  z-index: 30;
}

/* A header that stays gets a line under it once the layout has scrolled. */
.mvpl[data-mvpl-header-fixed] > .mvpl-grid > .mvpl-header {
  transition: box-shadow 0.15s ease;
}
.mvpl[data-mvpl-header-fixed][data-mvpl-scrolled] > .mvpl-grid > .mvpl-header {
  box-shadow: 0 1px 0 var(--mvpl-line, var(--color-base-300, color-mix(in oklab, CanvasText 15%, Canvas))), 0 1px 3px rgb(0 0 0 / 0.06);
}
.mvpl[data-mvpl-footer-fixed] > .mvpl-grid > .mvpl-footer {
  box-shadow: 0 -1px 0 var(--mvpl-line, var(--color-base-300, color-mix(in oklab, CanvasText 15%, Canvas)));
}

/* A sidebar beside the page. Its column is as wide as it is, so a closed
   sidebar, or one the page left empty, takes no space. */
.mvpl-grid > .mvpl-sidebar {
  --mvpl-w: 16rem;
  --mvpl-rail-w: 4rem;
  --mvpl-mode: docked;
  width: var(--mvpl-w);
  min-width: 0;
  background: var(--mvpl-sidebar-bg, var(--color-base-100, Canvas));
  transition: width 0.2s ease;
}
.mvpl-grid > .mvpl-sidebar[data-side="right"] { --mvpl-w: 18rem; }
.mvpl-grid > .mvpl-sidebar[data-side="left"] > .mvpl-panel {
  border-inline-end: 1px solid var(--mvpl-line, var(--color-base-300, color-mix(in oklab, CanvasText 15%, Canvas)));
}
.mvpl-grid > .mvpl-sidebar[data-side="right"] > .mvpl-panel {
  border-inline-start: 1px solid var(--mvpl-line, var(--color-base-300, color-mix(in oklab, CanvasText 15%, Canvas)));
}
.mvpl-grid > .mvpl-sidebar > .mvpl-panel {
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  width: var(--mvpl-w);
  min-height: 100%;
}
.mvpl-grid > .mvpl-sidebar > .mvpl-backdrop { display: none; }

.mvpl[data-mvpl-left-fixed] > .mvpl-grid > .mvpl-sidebar[data-side="left"] > .mvpl-panel,
.mvpl[data-mvpl-right-fixed] > .mvpl-grid > .mvpl-sidebar[data-side="right"] > .mvpl-panel {
  position: sticky;
  z-index: 20;
  min-height: 0;
  overflow-y: auto;
  scrollbar-width: thin;
}
.mvpl[data-mvpl-left-fixed] > .mvpl-grid > .mvpl-sidebar[data-side="left"] > .mvpl-panel {
  top: var(--mvpl-left-top);
  height: calc(var(--mvpl-vh) - var(--mvpl-left-top) - var(--mvpl-left-bottom));
}
.mvpl[data-mvpl-right-fixed] > .mvpl-grid > .mvpl-sidebar[data-side="right"] > .mvpl-panel {
  top: var(--mvpl-right-top);
  height: calc(var(--mvpl-vh) - var(--mvpl-right-top) - var(--mvpl-right-bottom));
}

/* A sidebar with nothing in its panel isn't drawn. The Cotton component leaves
   an empty sidebar out altogether; a template written by hand leaves its
   panel empty instead. */
.mvpl-grid > .mvpl-sidebar:has(> .mvpl-panel:empty) { display: none; }

/* Closed beside the page: slid away, or an icon rail. */
.mvpl-grid > .mvpl-sidebar[data-state="closed"][data-collapse="offcanvas"] {
  width: 0;
  overflow: clip;
}
.mvpl-grid > .mvpl-sidebar[data-state="closed"][data-collapse="offcanvas"] > .mvpl-panel {
  visibility: hidden;
  transition: visibility 0s linear 0.2s;
}
.mvpl-grid > .mvpl-sidebar[data-state="closed"][data-collapse="icons"] { width: var(--mvpl-rail-w); }
.mvpl-grid > .mvpl-sidebar[data-state="closed"][data-collapse="icons"] > .mvpl-panel {
  width: var(--mvpl-rail-w);
  overflow-x: hidden;
}

/* Content that is only for the open sidebar, or only for the rail. */
.mvpl-rail-only { display: none; }
.mvpl-sidebar[data-mvpl-rail] .mvpl-rail-hide { display: none !important; }
.mvpl-sidebar[data-mvpl-rail] .mvpl-rail-only { display: revert; }

/* The script hides a toggle with nothing to toggle. daisyUI's buttons set
   their own display, which would otherwise beat the hidden attribute. */
.mvpl-toggle[hidden],
[data-mvpl-when][hidden] { display: none !important; }

@media (prefers-reduced-motion: reduce) {
  .mvpl-grid > .mvpl-sidebar,
  .mvpl-grid > .mvpl-sidebar > .mvpl-panel,
  .mvpl-grid > .mvpl-sidebar > .mvpl-backdrop { transition: none !important; }
}

@media print {
  .mvpl-grid > .mvpl-sidebar { display: none; }
  .mvpl[data-mvpl-header-fixed] > .mvpl-grid > .mvpl-header,
  .mvpl[data-mvpl-footer-fixed] > .mvpl-grid > .mvpl-footer { position: static; }
}
"""

# One sidebar as a drawer over the page. {s} is the selector of the sidebar.
DRAWER = """\
{s} {{
  --mvpl-mode: overlay;
  width: 0;
  overflow: visible;
}}
{s} > .mvpl-panel {{
  position: fixed;
  top: 0;
  bottom: 0;
  z-index: 40;
  width: min(var(--mvpl-w), 100% - 3.5rem);
  height: auto;
  min-height: 0;
  overflow-y: auto;
  overscroll-behavior: contain;
  visibility: hidden;
  border-inline-width: 0;
  background: var(--mvpl-sidebar-bg, var(--color-base-100, Canvas));
  box-shadow: 0 0 2rem rgb(0 0 0 / 0.25);
  transition: translate 0.25s ease, visibility 0s linear 0.25s;
}}
{s}[data-side="left"] > .mvpl-panel {{
  inset-inline-start: 0;
  translate: calc(-100% * var(--mvpl-dir)) 0;
}}
{s}[data-side="right"] > .mvpl-panel {{
  inset-inline-end: 0;
  translate: calc(100% * var(--mvpl-dir)) 0;
}}
{s}[data-overlay="open"] > .mvpl-panel {{
  translate: 0 0;
  visibility: visible;
  transition: translate 0.25s ease, visibility 0s;
}}
{s} > .mvpl-backdrop {{
  display: block;
  position: fixed;
  inset: 0;
  z-index: 39;
  background: rgb(0 0 0 / 0.4);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.25s ease;
}}
{s}[data-overlay="open"] > .mvpl-backdrop {{
  opacity: 1;
  pointer-events: auto;
}}
{c} > .mvpl-panel,
{c} > .mvpl-backdrop {{
  position: absolute;
}}
"""


def drawer(sidebar: str) -> str:
    """Return the drawer rules for one sidebar selector, such as ``.mvpl-sidebar[...]``."""
    return DRAWER.format(
        s=f".mvpl > .mvpl-grid > {sidebar}",
        c=f".mvpl[data-mvpl-container] > .mvpl-grid > {sidebar}",
    )


def build() -> str:
    """Return the whole stylesheet."""
    parts = [
        BASE,
        "\n/* A sidebar whose behaviour is overlay is a drawer at every width. */\n",
    ]
    parts.append(drawer('.mvpl-sidebar[data-side][data-behavior="overlay"]'))
    for name, width in BREAKPOINTS.items():
        block = drawer(
            f'.mvpl-sidebar[data-side][data-behavior="auto"][data-breakpoint="{name}"]'
        )
        indented = "".join(
            f"  {line}" if line.strip() else line for line in block.splitlines(True)
        )
        parts.append(
            f"\n/* Below {width} of layout width, a sidebar with breakpoint {name} is a drawer. */\n"
            f"@container mvpl (width < {width}) {{\n{indented}}}\n"
        )
    return "".join(parts)


def main() -> None:
    """Write the stylesheet, or print it with ``--stdout``."""
    if "--stdout" in sys.argv:
        sys.stdout.write(build())
        return
    target = (
        Path(__file__).resolve().parent.parent
        / "mvp_layout"
        / "static"
        / "mvp_layout"
        / "layout.css"
    )
    target.write_text(build())
    print(f"wrote {target}")


if __name__ == "__main__":
    main()
