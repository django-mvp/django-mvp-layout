"""Write mvp_layout/static/mvp_layout/layout.css.

Run ``uv run python scripts/build_css.py`` after changing this script or
``scripts/layout.base.css``, and commit the result. A container query cannot take
its width from a custom property, so the drawer rules are written out once for
each breakpoint here rather than by hand.

The whole stylesheet is one cascade layer, ``mvpl``, so the host's own rules win
at any specificity and in any order. It opens with the statement
``@layer base, mvpl;`` so that a host's ``base`` layer, where Tailwind puts its
preflight, sorts below ``mvpl`` and cannot remove the package's borders. Layers the
host declares later sort above ``mvpl``.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE.parent / "mvp_layout" / "static" / "mvp_layout" / "layout.css"

# Declares the order of two layers before the package's own: a host's ``base`` layer
# (a host without one gets an empty layer) sorts below ``mvpl``.
LAYER_ORDER = "@layer base, mvpl;\n"

BREAKPOINTS = {
    "sm": "40rem",
    "md": "48rem",
    "lg": "64rem",
    "xl": "80rem",
    "2xl": "96rem",
}

# The rules that do not depend on a breakpoint, kept as a stylesheet of their own
# because its selectors do not fit on a line of Python.
BASE = (HERE / "layout.base.css").read_text()

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
  width: min(var(--mvpl-sidebar-w), 100% - 3.5rem);
  height: auto;
  min-height: 0;
  overflow-y: auto;
  overscroll-behavior: contain;
  visibility: hidden;
  margin-inline-start: 0;
  border-inline-width: 0;
  background: var(--mvpl-sidebar-bg, var(--color-base-100, Canvas));
  box-shadow: 0 0 2rem rgb(0 0 0 / 0.25);
  transition: translate var(--mvpl-transition, 0.25s) ease, visibility 0s linear var(--mvpl-transition, 0.25s);
}}
{s}[data-mvpl-side="left"] > .mvpl-panel {{
  inset-inline-start: 0;
  translate: calc(-100% * var(--mvpl-dir)) 0;
}}
{s}[data-mvpl-side="right"] > .mvpl-panel {{
  inset-inline-end: 0;
  translate: calc(100% * var(--mvpl-dir)) 0;
}}
{s}[data-mvpl-overlay="open"] > .mvpl-panel {{
  translate: 0 0;
  visibility: visible;
  transition: translate var(--mvpl-transition, 0.25s) ease, visibility 0s;
}}
{s} > .mvpl-backdrop {{
  display: block;
  position: fixed;
  inset: 0;
  z-index: 39;
  background: rgb(0 0 0 / 0.4);
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--mvpl-transition, 0.25s) ease;
}}
{s}[data-mvpl-overlay="open"] > .mvpl-backdrop {{
  opacity: 1;
  pointer-events: auto;
}}
{c} > .mvpl-panel,
{c} > .mvpl-backdrop {{
  position: absolute;
}}
"""


def drawer(sidebar: str) -> str:
    """Return the drawer rules for one sidebar selector.

    Args:
        sidebar: The sidebar's selector, such as ``.mvpl-sidebar[data-mvpl-side]``.

    Returns:
        The rules that draw the sidebar as a drawer over the page.
    """
    return DRAWER.format(
        s=f".mvpl > .mvpl-grid > {sidebar}",
        c=f".mvpl[data-mvpl-container] > .mvpl-grid > {sidebar}",
    )


def build() -> str:
    """Return the whole stylesheet, inside the ``mvpl`` cascade layer."""
    parts = [
        BASE,
        "\n/* A sidebar whose behaviour is overlay is a drawer at every width. */\n",
        drawer('.mvpl-sidebar[data-mvpl-side][data-mvpl-behavior="overlay"]'),
    ]
    for name, width in BREAKPOINTS.items():
        block = drawer(
            ".mvpl-sidebar[data-mvpl-side][data-mvpl-behavior="
            f'"auto"][data-mvpl-breakpoint="{name}"]'
        )
        indented = "".join(
            f"  {line}" if line.strip() else line for line in block.splitlines(True)
        )
        parts.append(
            f"\n/* Below {width} of layout width, a sidebar with breakpoint {name} "
            f"is a drawer. */\n@container mvpl (width < {width}) {{\n{indented}}}\n"
        )
    return LAYER_ORDER + "@layer mvpl {\n" + "".join(parts) + "}\n"


def main() -> None:
    """Write the stylesheet, or print it with ``--stdout``."""
    if "--stdout" in sys.argv:
        sys.stdout.write(build())
        return
    TARGET.write_text(build())
    print(f"wrote {TARGET}")


if __name__ == "__main__":
    main()
