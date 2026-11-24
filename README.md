# django-mvp-layout

[![Tests](https://github.com/django-mvp/django-mvp-layout/actions/workflows/tests.yml/badge.svg)](https://github.com/django-mvp/django-mvp-layout/actions/workflows/tests.yml)
[![Build](https://github.com/django-mvp/django-mvp-layout/actions/workflows/build.yml/badge.svg)](https://github.com/django-mvp/django-mvp-layout/actions/workflows/build.yml)
[![Docs](https://github.com/django-mvp/django-mvp-layout/actions/workflows/docs.yml/badge.svg)](https://github.com/django-mvp/django-mvp-layout/actions/workflows/docs.yml)
[![Publish](https://github.com/django-mvp/django-mvp-layout/actions/workflows/publish.yml/badge.svg)](https://github.com/django-mvp/django-mvp-layout/actions/workflows/publish.yml)
[![Coverage](https://codecov.io/gh/django-mvp/django-mvp-layout/branch/main/graph/badge.svg)](https://codecov.io/gh/django-mvp/django-mvp-layout)
[![PyPI](https://img.shields.io/pypi/v/django-mvp-layout)](https://pypi.org/project/django-mvp-layout/)
[![Development status](https://img.shields.io/pypi/status/django-mvp-layout)](https://pypi.org/project/django-mvp-layout/)
[![Python](https://img.shields.io/pypi/pyversions/django-mvp-layout)](https://pypi.org/project/django-mvp-layout/)
[![Django](https://img.shields.io/pypi/djversions/django-mvp-layout)](https://pypi.org/project/django-mvp-layout/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Licence](https://img.shields.io/github/license/django-mvp/django-mvp-layout)](https://github.com/django-mvp/django-mvp-layout/blob/main/LICENSE)

Page layouts arranged by a nine-letter layout code, with sidebars that open, close, collapse and nest.

```html
<c-layout view="lHh LpR lff">
  <c-layout.header>…</c-layout.header>
  <c-layout.sidebar side="left" collapse="icons" persist="nav" label="Navigation">…</c-layout.sidebar>
  <c-layout.page tag="main">…</c-layout.page>
  <c-layout.sidebar side="right" label="On this page">…</c-layout.sidebar>
  <c-layout.footer>…</c-layout.footer>
</c-layout>
```

## Scope & philosophy

The package arranges a header, two sidebars, a page and a footer, and makes the sidebars behave:
they open and close, shrink to an icon rail, become drawers on a narrow layout, and remember their
state. A layout is a page or a box inside one, and it nests inside itself. The package renders markup
and ships one stylesheet and one script. It has no models, views, URLs or settings, and it leaves the
look of everything inside the areas to the host project.

It works with or without [django-cotton](https://django-cotton.com) components, and with or without
daisyUI, whose theme colours it uses when they are there.

When two designs conflict, the one that keeps a layout accessible and its markup readable wins over
the one with more options.

## Installation

```bash
pip install django-mvp-layout
```

```python
INSTALLED_APPS = [
    # ...
    "django_cotton",
    "mvp_layout",
]

TEMPLATES = [{
    # ...
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",  # reads a sidebar's remembered state
        # ...
    ]},
}]
```

## Quickstart

In the base template's head, without `defer`:

```html
{% load static %}
<link rel="stylesheet" href="{% static 'mvp_layout/layout.css' %}" />
<script src="{% static 'mvp_layout/layout.js' %}"></script>
```

Then lay out the body with the components, as above, or with the template tags in a plain base
template. [`docs/examples/base.html`](https://github.com/django-mvp/django-mvp-layout/blob/main/docs/examples/base.html)
is one to copy.

Write the areas in reading order: header, left sidebar, page, right sidebar, footer. The code places
them on screen, but screen readers and the Tab key follow the markup.

## Documentation

- [The layout code](https://django-mvp.github.io/django-mvp-layout/developer/layout-code.html): how a code reads, and why the order in the markup matters
- [Using the components](https://django-mvp.github.io/django-mvp-layout/developer/cotton.html): every component and attribute, drawers, nesting
- [Without django-cotton](https://django-mvp.github.io/django-mvp-layout/developer/without-cotton.html): a plain base template and the two template tags
- [Styling](https://django-mvp.github.io/django-mvp-layout/developer/styling.html): colours, sizes, the Tailwind rail variant, and how the stylesheet stays out of the way

## Public surface

**Components:** `<c-layout>`, `<c-layout.header>`, `<c-layout.sidebar>`, `<c-layout.page>`,
`<c-layout.footer>`, `<c-layout.toggle>`.

**Template tags** (`{% load mvp_layout %}`): `layout_attrs`, `sidebar_attrs`, `layout_view`,
`layout_uid`.

**Python:** `mvp_layout.view.LayoutView` and `LayoutViewError`, and
`mvp_layout.templatetags.mvp_layout.LayoutOptionError`.

**Static files:** `mvp_layout/layout.css` and `mvp_layout/layout.js`.

**Script:** `MvpLayout("app")` mounts the layout with that id and returns it. The same function
carries `MvpLayout.sync`, `state`, `toggle(layout, side)`, `open(layout, side)` and
`close(layout, side)`, each taking a layout's id or its element. A `mvpl:change` event fires on the
layout each time it settles its sidebars, carrying its state as its detail.

**Markup:** the `mvpl-*` classes, the `data-mvpl-*` attributes and the `--mvpl-*` variables listed in
the docs, and the `mvpl-<name>` cookies.

## What it leaves to the host project

- **Everything inside the areas.** The package draws no navigation, title or menu.
- **The theme.** Colours come from the host's daisyUI theme or from the system colours.
- **The drawer's breakpoint is the layout's width**, not the window's. A layout in a narrow card has
  drawers on a wide screen, which is the point, and can surprise.
- **A wrong layout code or sidebar option raises** at render time. Nothing falls back silently.

## Contributing

Standards for this repository live in
[CONSTITUTION.md](https://github.com/django-mvp/django-mvp-layout/blob/main/CONSTITUTION.md),
and the vocabulary to use in issues and commits lives in
[CONTEXT.md](https://github.com/django-mvp/django-mvp-layout/blob/main/CONTEXT.md).

```bash
uv sync
uv run playwright install chromium
uv run pytest
uv run pre-commit install
```

`demo/` is a Django project for looking at the package in a browser. It has no database:

```bash
uv run python manage.py runserver
```

The stylesheet is written by `scripts/build_css.py` and committed. After changing the script, run
`uv run python scripts/build_css.py`; a test fails while the committed file is out of date. The
demo's own stylesheet is Tailwind and daisyUI, built with `npm install && npm run build:css`.

## License

MIT. See [LICENSE](https://github.com/django-mvp/django-mvp-layout/blob/main/LICENSE).
