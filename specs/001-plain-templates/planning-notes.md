# Planning notes: Layouts in plain templates

Notes for research and planning. Each is answered by name in `research.md`.

## The prototype

This feature comes from the prototype on the `prototype-layout` branch. Its plan is
`PROTOTYPE.md` on that branch, and this feature is its feature 1, "Layouts in plain templates". It
also takes every item under "Faked or skipped" there. The prototype's screens and the decisions
under "Decisions" and "Decided on my own" are agreed, and the specification describes what they do.

## Shared pieces

The layout-code parser (`mvp_layout/view.py`), the sidebar options and the cookie
(`mvp_layout/templatetags/mvp_layout.py`), the stylesheet and its build script
(`scripts/build_css.py` → `mvp_layout/static/mvp_layout/layout.css`), the script
(`mvp_layout/static/mvp_layout/layout.js`) and `docs/examples/base.html` are all built by this
feature. The Cotton components that follow reuse them and build none of their own. Research
answers each by name: where it lands, what it exposes, and what the components will call.

## The look is ported, never redrawn

The files under "The look" in `PROTOTYPE.md` land at the same paths on `main`. This feature ports
`mvp_layout/static/mvp_layout/layout.css`, `scripts/build_css.py`,
`mvp_layout/static/mvp_layout/layout.js` and `docs/examples/base.html`. The plan names each file it
ports, and the design review fails a plan that redraws something the prototype already has. The
Cotton templates and the demo pages are not this feature's.

## Right-to-left: `left` and `right`, or `start` and `end`

Decide it in research from what Quasar's `view` and `QDrawer` do in right-to-left and from CSS
logical-property practice, and record the decision. It covers the sidebar's `side`,
`data-mvpl-toggle`, `data-mvpl-when` and the code's `l` and `r`. Then test right-to-left in a
browser at both widths and document it. The prototype already mirrors with `dir="rtl"`.

## The rest of "Faked or skipped"

- The script type-checked with `// @ts-check`, JSDoc types and a `tsc --noEmit` hook.
- Focus trapped in a drawer in a contained layout, not only the layout's own areas made inert.
- Width transitions on docked sidebars measured on a heavy page (SC-005).
- Browser tests beyond the demo pages, on test pages of their own.

## Documentation from the prototype

The prototype's `docs/developer/layout-code.md`, `without-cotton.md` and `styling.md` are the
starting point for this feature's pages. They link to the Cotton components' page, which does not
exist until the next feature, so those links are rewritten or left out here.
