# Implementation Plan: Layouts in plain templates

**Branch**: `001-plain-templates` | **Spec**: [spec.md](./spec.md) | **Research**: [research.md](./research.md)

## Summary

Port the prototype's stylesheet, script and base template, and rebuild its two Python modules
test-first, so a developer lays out a page in a plain Django template with two tags and the
documented base template. Three stories, built in order: the layout and its tags (US1), the
sidebars' behaviour for a person using the site (US2), and the script interface (US3). No models,
views, URLs or settings are added to the package.

## Technical Context

- **Language**: Python 3.12+, Django 5.2, 6.0 and 6.1. Plain JavaScript (ES2020) with no build step.
- **Runtime dependencies**: `django>=5.2` and `django-cotton>=2.9` only. `django-mvp` leaves the
  runtime list and joins the development group, because the demo project still runs on its shell
  (FR-023, Article XII).
- **New development tooling**: `typescript`, installed by a local pre-commit hook in its own node
  environment. `pytest-playwright` is already in the dev group.
- **Testing**: `pytest` for rendered output, the parser and the stylesheet check. `pytest-playwright`
  (Chromium) for everything a browser decides, on test pages of this repository's own.
- **Project type**: an installable Django package plus a demo project that is never deployed. The
  demo is untouched.

## Files

Created or ported (paths are repository-relative):

| Path | What | Source |
|---|---|---|
| `mvp_layout/view.py` | layout code parser | rebuilt from the prototype |
| `mvp_layout/templatetags/__init__.py`, `mvp_layout/templatetags/mvp_layout.py` | `layout_attrs`, `sidebar_attrs`, option errors, cookie read | rebuilt from the prototype |
| `scripts/build_css.py` | stylesheet generator | ported |
| `mvp_layout/static/mvp_layout/layout.css` | generated stylesheet | generated, byte-identical to the prototype's apart from its header comment |
| `mvp_layout/static/mvp_layout/layout.js` | the behaviour and `MvpLayout` | ported, then typed and extended |
| `docs/examples/base.html` | documented base template | ported |
| `tests/test_view.py`, `tests/test_templatetags/test_mvp_layout.py`, `tests/test_build_css.py`, `tests/test_layout_js.py` | tests | written test-first, prototype's browser tests used as the starting point |
| `tests/templates/layouts/*.html`, `tests/urls.py`, `tests/settings.py` | test pages of their own | new |
| `tsconfig.json`, `.pre-commit-config.yaml` | type check hook, with the compiler pinned | new and edited |
| `pyproject.toml`, `uv.lock` | dependencies, conformance paths | edited |
| `README.md`, `CHANGELOG.md` | first public API | edited |
| `docs/developer/layout-code.md`, `plain-templates.md`, `styling.md`, `scripting.md`, `right-to-left.md`, `index.md` | documentation | written from the prototype's pages |

Not touched: `demo/`, `mvp_layout/templates/` (feature 2), `.github/`.

## Design

### The tags and the parser (US1)

`LayoutView.parse` keeps the prototype's shape rules and refusal text, and returns the fields the
tags need: the normalised code, the `grid-template-areas` value, each area's fixed flag and the
offsets a fixed sidebar sticks at. The `explain` method and the four `*_reaches_*` fields that only
it reads are not ported. A missing code parses as `hHh lpr fFf`. Extra spaces between
groups are collapsed before the shape is checked.

`layout_attrs(view, container, css_class, style)` and
`sidebar_attrs(context, side, collapse, breakpoint, behavior, persist, closed, width, rail_width,
css_class)` write the attributes the stylesheet and script read. They are the prototype's with one change:
every `data-` attribute is prefixed `data-mvpl-` (`data-side` becomes `data-mvpl-side`, and
`collapse`, `breakpoint`, `behavior`, `state` and `persist` the same), because FR-022 requires it.
The script's own `data-overlay` and `data-mode` become `data-mvpl-overlay` and `data-mvpl-mode`.
Settling the options and reading the cookie are classmethods on the `Sidebar` dataclass
(`Sidebar.settle(...)`) that the tag calls. There is no base class or registry. A choice outside its allowed
values raises `LayoutOptionError` naming the choices. The remembered state is read from
`request.COOKIES["mvpl-<persist>"]` when a request is in the context, ignored when it is neither
`open` nor `closed`, and overridden by the sidebar's own options (`collapse="none"` is always open).

### The stylesheet (US1)

`scripts/build_css.py` is ported. A test runs it with `--stdout` and compares with the committed
file, which is FR-024's check. Because the look is ported, the test of the port itself compares the
generated file with `git show origin/prototype-layout:…` during the build and records the diff in
the task evidence. That comparison is a build-time check, never a committed test.

The generator differs from the prototype's in two named ways, and the build records each as a diff:
the attribute names in its selectors, and the whole output wrapped in `@layer mvpl { … }` so a
host's rules win at any specificity and in any order (US1 scenario 11). Everything else is the
prototype's, and the stylesheet needs no change for right-to-left: it already uses logical
properties and `--mvpl-dir`.

### The base template and test pages (US1)

`docs/examples/base.html` is ported with three changes: the stylesheet link comes before the
`styles` block so the host's layers follow the package's, the two `aria-label`s are wrapped in
`{% translate %}`, and its comment is rewritten. Test pages under
`tests/templates/layouts/` extend it through `docs/` added to the template search path in
`tests/settings.py` (so the name is `examples/base.html`, which cannot collide with the demo's
`base.html`). One page per situation a browser test needs: the default layout, a contained layout,
nested layouts, a contained layout in a narrow box on a wide window, an empty aside, a toggle
outside its layout, a right-to-left page, and a heavy page for SC-005. Routes live in
`tests/urls.py`.

### The behaviour (US2)

`layout.js` is ported with the layout in the first story, so every page the first story shows loads
it without an error. It is then covered by browser tests, each shown to fail when its behaviour is
removed from the script (the mutation is recorded in the task's evidence). The prototype's
`MvpLayout.mount` alias is not ported. The
behaviour that is new in this feature is a Tab trap inside an open drawer, so that focus stays in a
contained layout's drawer too (FR-013). The drawer and its modal behaviour are the prototype's:
`inert` on the layout's other areas, `role="dialog"` and `aria-modal` on the panel, the page
locked behind a whole-page drawer, the wheel kept only by an open drawer.

### The script interface (US3)

`MvpLayout(<id or element>)`, `.sync`, `.state`, `.toggle`, `.open`, `.close` and the `mvpl:change`
event exist in the port. This story adds what the specification demands that the prototype does not
give: an error naming an id that matches no layout (scenario 7), and the type check. The prototype
calls with an unknown id and does nothing or returns `null`.

## Constitution check

The repository's rules that bear on this plan: tests mirror the source tree (the three browser and
stylesheet modules are declared under `non-mirror-paths`), no leading-underscore names, 88-character
lines, no compatibility aliases, no test of wording or design preferences, every public name
documented.

## What already exists

See `research.md`, `## What already exists`.

## Risks

- **SC-005** may fail on the width transition. If so the sidebar's animation is changed (for
  example from `width` to a transform of the panel) and the reason recorded in `decisions.md`.
- **Chromium in CI**: the shared tests workflow installs it through its `install-playwright` input,
  which the `chromium` fixture already depends on.
