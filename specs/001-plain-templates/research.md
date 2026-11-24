# Research: Layouts in plain templates

## Assumptions checked

Checked on 2026-11-24, before the specification was put up for approval, against the prototype running at port 8066
and against `main`.

- **The tags render a layout in a plain template.** The prototype's page extending
  `docs/examples/base.html` returns 200 and carries `data-mvpl-view="hHh LpR fFf"` on its root and
  `data-persist` on both sidebars. Holds.
- **The server draws the remembered state.** The same page requested with the cookie
  `mvpl-nav=closed` renders the navigation sidebar with `data-state="closed"` and the other open.
  Holds.
- **`main`'s test settings have the request context processor.** `demo/settings.py`, which
  `tests/settings.py` inherits, lists `django.template.context_processors.request`. Holds.
- **The browser test tooling exists.** The prototype's `pyproject.toml` already carries
  `pytest-playwright` and its `tests/test_layout_js.py` runs in Chromium. `main` has neither yet,
  so the build adds them.
- **A TypeScript checker for `tsc --noEmit`.** Neither branch's `package.json` has `typescript`.
  The build adds it as a development dependency.
