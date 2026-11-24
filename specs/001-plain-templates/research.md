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
- **The browser test tooling exists.** `main` already carries `pytest-playwright` in its dev group
  and a `chromium` fixture in `tests/conftest.py`. The prototype's `tests/test_layout_js.py` runs in
  Chromium on the same tooling. Holds.
- **A TypeScript checker for `tsc --noEmit`.** `main` has no `package.json`, and the prototype's
  carries only the demo's stylesheet tooling. The build adds `typescript` through a pre-commit hook
  that installs its own node environment.

## Planning notes answered

### The prototype (adopted)

Read `PROTOTYPE.md` and every file under "The look" for this feature. The pages Sam reacted to are
the agreed design. Logic is rebuilt test-first, and the markup and styles are ported.

### Shared pieces (adopted)

Where each lands, what it exposes, and what the Cotton components will call:

| Piece | Lands in | Exposes | The components call |
|---|---|---|---|
| Layout code parser | `mvp_layout/view.py` | `LayoutView.parse(code)`, `LayoutViewError` | `{% layout_attrs %}` |
| Sidebar options and cookie | `mvp_layout/templatetags/mvp_layout.py` | `{% layout_attrs %}`, `{% sidebar_attrs %}`, `LayoutOptionError` | both tags |
| Stylesheet | `scripts/build_css.py` writes `mvp_layout/static/mvp_layout/layout.css` | the `mvpl` classes, variables and data attributes | loaded by the host's base template |
| Script | `mvp_layout/static/mvp_layout/layout.js` | `MvpLayout`, `mvpl:change` | loaded by the host's base template |
| Base template | `docs/examples/base.html` | blocks `title`, `styles`, `header`, `navigation`, `content`, `aside`, `footer` | none, it is documentation |

The prototype's `explain()` method on the layout code, `layout_view` tag and `layout_uid` tag have
no requirement in this specification. `explain()` serves the demo's playground. `layout_view` has
no caller once `layout_attrs` reads the code, and `layout_uid` serves components that need an id.
They are left out and the feature that needs one adds it.

### The look is ported, never redrawn (adopted)

Ported from `origin/prototype-layout`: `mvp_layout/static/mvp_layout/layout.css` (through
`scripts/build_css.py`, which is copied and cleaned and its output kept byte-for-byte except for
its header comment), `mvp_layout/static/mvp_layout/layout.js`, `docs/examples/base.html`, and the
logic of `mvp_layout/view.py` and `mvp_layout/templatetags/mvp_layout.py`, rebuilt test-first. Not
ported: the Cotton templates (feature 2) and `demo/` (issue 5).

### `left` and `right`, or `start` and `end` (decided: `left` and `right`)

Quasar's `QDrawer` takes `side` as `'left'` or `'right'`, and Quasar's right-to-left support
(`postcss-rtlcss`) swaps what those mean when the document is right-to-left. Its `QLayout` `view`
reads `l` and `r` the same way. This package's code letters are Quasar's, so a code written for one
works in the other, and the prototype's grid already follows the writing direction with logical
properties. Renaming only the `side` option to `start` and `end` would leave the code's `l` and `r`
meaning the start and end side under a different name, which breaks FR-021's rule that one name means
one side everywhere. Renaming the letters to `s` and `e` would end compatibility with Quasar's codes.

CSS logical properties favour `start` and `end` for new CSS, and the stylesheet already uses them
(`inset-inline-start`, `border-inline-end`) for everything it draws. Only the public names stay
`left` and `right`.

**Decision**: keep `left` and `right`. They name the sidebar on the reading start side and the
reading end side. In a left-to-right document `left` is drawn at the left. In a right-to-left
document `left` is drawn at the right, and its drawer slides in from the right. The documentation
says so in each place a side is named. No public name changes, so FS-002 builds on `left` and
`right` unchanged.

### The rest of "Faked or skipped" (adopted)

- **Type check**: `// @ts-check` and JSDoc in `layout.js`, a `tsconfig.json` with `checkJs` and
  `noEmit`, and a local pre-commit hook of `language: node` with `typescript` as its additional
  dependency, so the hook installs its own compiler in CI and in the shared Code Quality job with no
  `npm ci`. the Code Quality job in CI runs `pre-commit run --all-files`, so the type check is one of the
  repository's checks. The compiler is pinned to one version in the hook, and it lives in the hook
  rather than the shared development bundle because no Python package ships `tsc`.
- **Focus trap in a contained layout**: a `keydown` handler on Tab inside an open drawer wraps
  focus between the drawer's first and last focusable elements. The inert siblings alone do not
  stop focus leaving a contained layout, because the browser's own chrome and the rest of the page
  stay reachable.
- **Width transitions**: measured in a browser test with a `PerformanceObserver` of `longtask`
  entries on a heavy page, SC-005.
- **Browser tests beyond the demo pages**: test pages under `tests/templates/layouts/`, extending
  `docs/examples/base.html`, routed in `tests/urls.py`.

## What already exists

- Layout code parser: the prototype's `view.py` (port, rebuilt test-first, `explain` left out).
- Sidebar options and cookie: the prototype's tag module (port, rebuilt test-first).
- Request cookie reading: Django's `request.COOKIES`. Nothing new.
- Stylesheet generation: the prototype's `scripts/build_css.py` (port, the output is checked
  byte-for-byte against the prototype's committed stylesheet).
- Drawers' focus containment, scroll lock and inert regions: the platform's `inert` attribute and
  `aria-modal`, as the prototype uses them. The native `<dialog>` element was considered and not
  adopted, because a drawer is an `<aside>` that is also docked beside the page at wide widths and
  `showModal()` cannot be applied to an element that is not currently a dialog without moving it.
- Script type check: `typescript`'s `tsc` through pre-commit's node environment (a maintained
  package).
- Browser tests: `pytest-playwright`, already in the dev group, and the `chromium` fixture already
  in `tests/conftest.py`.
- Long-task measurement: the browser's `PerformanceObserver` (the browser).
- Container queries for the breakpoints: CSS (the browser). Nothing is scripted.
- Cookie writing: `document.cookie`. Nothing new.
- Tab trap in an open drawer (FR-013) and the error for an id that names no layout (US3 scenario
  7): new code. Neither the platform nor the tree has an equivalent. `inert` keeps focus out of the
  layout's other areas but does not wrap Tab inside the drawer, and the prototype's functions return
  `null` for an unknown id.
- Keeping host rules ahead of the package's: CSS cascade layers (the browser). The stylesheet is
  one `@layer mvpl` block, so a host's unlayered rule wins at any specificity.

## Changes the design review required

- **Every data attribute starts with `mvpl` (FR-022).** The prototype writes `data-side`,
  `data-collapse`, `data-breakpoint`, `data-behavior`, `data-state`, `data-persist`,
  `data-overlay` and `data-mode`. They become `data-mvpl-side` and so on in the tags, the generated
  stylesheet and the script. Nothing is redrawn: the computed styles are the same, and the
  side-by-side comparison with the prototype proves it.
- **A host's rules on the package's classes take effect (US1 scenario 11).** The prototype's rules
  are unlayered and several have high specificity, so a host's `.mvpl-sidebar { … }` loses. The
  generator wraps its output in `@layer mvpl`, and the base template links the stylesheet before
  its `styles` block so the host's own layers come after the package's.
- **The package depends on Django and django-cotton and nothing else at runtime (FR-023,
  Article XII).** `main` still lists django-mvp as a dependency, which pulls in daisy-cotton and
  the rest of that stack. The prototype settled this, and this feature takes its dependency list.
  django-mvp moves to the development group, because the demo project still runs on its shell.
- **The width transition is measured with `long-animation-frame` entries**, not `longtask`.
  Long tasks leave out rendering work, which is where a width transition's cost falls.
