# Planning notes — 002, layouts with Cotton components

Notes for whoever plans and builds this feature. Each one is answered by name in the research.

**The prototype.** This feature comes from the `prototype-layout` branch. Its `PROTOTYPE.md` describes
it as feature 2, "Layouts with Cotton": `<c-layout>`, `<c-layout.header>`, `<c-layout.page>`,
`<c-layout.footer>`, `<c-layout.sidebar>`, `<c-layout.toggle>`, and nesting with `container`. Its
screens and the decisions recorded in `PROTOTYPE.md` ("Decisions" and "Decided on my own") are
agreed. The demo runs on http://devserver:8066/ (overview, /playground/, /nested/, /without-cotton/).

**Shared pieces.** The layout-code parser (`mvp_layout/view.py`), the sidebar options and the cookie
(`mvp_layout/templatetags/mvp_layout.py`), the stylesheet and its build script (`scripts/build_css.py`
→ `mvp_layout/static/mvp_layout/layout.css`), the script (`mvp_layout/static/mvp_layout/layout.js`)
and `docs/examples/base.html` are all built by FS-001. FS-002 reuses them and builds none of its own.

**The look is ported, never redrawn.** The files under "The look" in `PROTOTYPE.md` land at the same
paths in `main`. This feature ports `mvp_layout/templates/cotton/layout/*.html` (`index.html`,
`header.html`, `page.html`, `footer.html`, `sidebar.html`, `toggle.html`), and the plan names each of
them. A plan that redraws something the prototype already has fails the design review.

**The id tag.** The prototype's components generate ids with `{% layout_uid %}`, which lives in the
same tags file as `layout_attrs` and `sidebar_attrs`. It is part of the tags FS-001 ports. If FS-001
lands without it, it is added to that tags file, not to a file of this feature's own.

**The developer page.** The prototype's `docs/developer/cotton.md` is the components page. Port it,
and cut anything it says about behaviour that FS-001's pages already document, linking there instead.

**The dependency.** The prototype declares `django-cotton>=2.9` and drops `django-mvp` as a
dependency. Check what FS-001 left in `pyproject.toml`. The components need django-cotton declared.
The package template's sample component (`cotton/mvp_layout/example.html`) is removed by the demo
work (issue #5), not here.

**Left and right.** If FS-001 renames `left` and `right` to `start` and `end` for right-to-left, the
components follow: `side`, the toggle's default accessible name, and the default icon's orientation.
