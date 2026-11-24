# Implementation Plan: Layouts with Cotton components

**Branch**: `002-cotton-components` | **Spec**: [spec.md](./spec.md) | **Research**: [research.md](./research.md)

## Summary

Port the prototype's six Cotton templates to the same paths and clean them to the repository's
standards, add the one tag they need that the plain-template feature left out (`layout_uid`), and
test that a component layout carries the same attributes as a plain-template layout. Two stories in
order: a page laid out with components (US1), then a box inside a page (US2). No models, views, URLs
or settings are added. The stylesheet and script are not changed. The two attribute tags change in one place: an empty `persist` means none given (design review DR-001).

## Technical Context

- **Language**: Python 3.12+, Django 5.2 to 6.1, django-cotton 2.9.
- **Runtime dependencies**: unchanged (`django>=5.2`, `django-cotton>=2.9`).
- **Testing**: `pytest` rendering real template files through Cotton, and `pytest-playwright`
  (Chromium) for the one behaviour a browser decides: that a component page opens, closes and mounts
  as a plain-template page does.
- **Project type**: an installable Django package. The demo is untouched (issue #5).

## Files

| Path | What | Source |
|---|---|---|
| `mvp_layout/templates/cotton/layout/index.html` | `<c-layout>` | ported |
| `mvp_layout/templates/cotton/layout/header.html` | `<c-layout.header>` | ported |
| `mvp_layout/templates/cotton/layout/page.html` | `<c-layout.page>` | ported |
| `mvp_layout/templates/cotton/layout/footer.html` | `<c-layout.footer>` | ported |
| `mvp_layout/templates/cotton/layout/sidebar.html` | `<c-layout.sidebar>` | ported |
| `mvp_layout/templates/cotton/layout/toggle.html` | `<c-layout.toggle>` | ported |
| `mvp_layout/templatetags/mvp_layout.py` | gains `layout_uid` (no default prefix, with its docstring); `Sidebar.settle` treats an empty `persist` as none given | new and edited |
| `mvp_layout/locale/` | the base English catalogue for the toggle's default names | new |
| `tests/test_templatetags/test_mvp_layout.py` | `TestLayoutUid` | written test-first |
| `tests/test_components/` | rendered-attribute tests, one module per component, and a browser test | written test-first |
| `tests/templates/components/*.html` | test pages that use the components | new |
| `tests/urls.py` | routes for the component test pages the browser test loads | edited |
| `docs/developer/cotton.md`, `docs/developer/index.md` | the components page | ported from the prototype, cut to what is not documented elsewhere |
| `pyproject.toml` | `tests/test_components/` added to the non-mirror paths | edited |
| `README.md`, `CHANGELOG.md` | the components are public API | edited |

Not touched: `demo/`, the stylesheet, the script, `docs/examples/base.html`, `.github/`.

## Design

### Components are templates, tags write the attributes (US1)

Each component is the prototype's file. Every attribute a layout, sidebar or toggle carries is
written by `layout_attrs`, `sidebar_attrs` or, for the toggle, by the markup the script reads
(`data-mvpl-toggle`, `data-mvpl-when`, `aria-expanded`). The components add `class` and `style`
to the tags through their `css_class` and `style` arguments, and every other attribute through
Cotton's `{{ attrs }}`. Component templates carry `@description`, `@prop` and `@slot` comments, the
form django-mvp's Cotton component documentation reads, so each component's attributes are documented
on the component itself (FR-014).

Cleaning the port to the repository's standards means:

- no name starts with an underscore and no `{% include %}` partial is used (none is in the prototype);
- the sidebar's `<c-vars>` defaults for `side`, `collapse` and `behavior` are empty, so the tag owns the defaults;
- the mount script writes the id with `escapejs`;
- the toggle's default names go through `{% translate %}` (Article VIII), with the English catalogue shipped;
- the page component's two branches share one attribute string so a new attribute is not edited twice;
- the wording of the `@prop` comments matches `docs/developer/cotton.md`.

Anything else that differs from `git diff origin/prototype-layout HEAD --
mvp_layout/templates/cotton/layout/` is a defect to fix at the browser pass.

### Unique ids (FR-003, FR-008)

`layout_uid(prefix="mvpl")` returns `f"{prefix}-{uuid.uuid4().hex[:12]}"`. A component with no `id` calls
`{% layout_uid "layout" as id %}` and `{% layout_uid "sidebar" as id %}`. A given `id` is used as
written. Random ids differ between two renders of one page, which the spec allows (edge case: unique
within each render). A test that needs a stable id gives one.

### Tests (US1, US2)

Tests render component source with the suite's existing `render` fixture (`tests/conftest.py`), passing
`request=` for the cookie case. The attribute reader that already exists in `tests/test_templatetags/test_mvp_layout.py`
moves to `tests/conftest.py` to be shared. `tests/templates/components/` holds only the pages the browser tests load. The parity tests (SC-002) render the same
options through the component and through the tags in one template file, and compare the
attributes of the layout, sidebar and toggle elements parsed from both, ignoring ids and comparing classes as sets. The toggle has no tag, so its parity side is FS-001's own plain toggles in `tests/templates/layouts/toggles.html`, never markup written for the test. One parametrised
case per option and per illegal value. The browser test loads a component page and its plain-template
counterpart and compares the state after opening, closing and a drawer at a narrow width.

### Documentation (US1)

`docs/developer/cotton.md` is ported and cut. Each component's `<c-vars>` names, its `@prop` names and the page's table names must be the same set (SC-003), so `class`, `style` and `id` are declared and documented too, so a new attribute fails it until it
is documented.

## Constitution and standards check

- Cotton components, never `{% include %}` partials. Pass.
- No leading-underscore names, line length 88 in Python. Pass, and the pre-commit run enforces it.
- No test of text content or design: tests compare attributes and structure, never copy or widths.
- No compatibility aliases: the prototype's `layout_view` and `MvpLayout.mount` are not reintroduced.

## Complexity tracking

None. The only code beyond templates is a three-line tag.

## Stories and order

1. **US1**: the id tag, the five templates, the toggle, the parity tests, the browser test, the page.
2. **US2**: the nested tests. Component behaviour needs no new template.
