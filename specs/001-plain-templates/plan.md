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
- **New runtime dependencies**: none. `django-cotton` stays a runtime dependency, unused by this
  feature.
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
| `tsconfig.json`, `.pre-commit-config.yaml`, `pyproject.toml` | type check hook, conformance paths | edited |
| `docs/developer/layout-code.md`, `plain-templates.md`, `styling.md`, `scripting.md`, `right-to-left.md`, `index.md` | documentation | written from the prototype's pages |

Not touched: `demo/`, `mvp_layout/templates/` (feature 2), `.github/`.

## Design

### The tags and the parser (US1)

`LayoutView.parse` keeps the prototype's shape rules and refusal text, and returns the fields the
tags need: the normalised code, the `grid-template-areas` value, each area's fixed flag and the
offsets a fixed sidebar sticks at. A missing code parses as `hHh lpr fFf`. Extra spaces between
groups are collapsed before the shape is checked.

`layout_attrs(view, container, css_class, style)` and
`sidebar_attrs(context, side, collapse, breakpoint, behavior, persist, closed, width, rail_width,
css_class)` write the attributes the stylesheet and script read, exactly as the prototype writes
them, so the generated stylesheet and the script need no change. A choice outside its allowed
values raises `LayoutOptionError` naming the choices. The remembered state is read from
`request.COOKIES["mvpl-<persist>"]` when a request is in the context, ignored when it is neither
`open` nor `closed`, and overridden by the sidebar's own options (`collapse="none"` is always open).

### The stylesheet (US1)

`scripts/build_css.py` is ported. A test runs it with `--stdout` and compares with the committed
file, which is FR-024's check. Because the look is ported, the test of the port itself compares the
generated file with `git show origin/prototype-layout:…` during the build and records the diff in
the task evidence. That comparison is a build-time check, never a committed test.

The stylesheet needs no change for right-to-left: the prototype already uses logical properties
and `--mvpl-dir`.

### The base template and test pages (US1)

`docs/examples/base.html` is ported unchanged apart from its comment. Test pages under
`tests/templates/layouts/` extend it through `docs/` added to the template search path in
`tests/settings.py` (so the name is `examples/base.html`, which cannot collide with the demo's
`base.html`). One page per situation a browser test needs: the default layout, a contained layout,
nested layouts, a contained layout in a narrow box on a wide window, an empty aside, a toggle
outside its layout, a right-to-left page, and a heavy page for SC-005. Routes live in
`tests/urls.py`.

### The behaviour (US2)

`layout.js` is ported and each behaviour it already has is covered by a browser test first. The
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
