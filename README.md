# django-mvp-layout

[![Tests](https://github.com/django-mvp/django-mvp-layout/actions/workflows/tests.yml/badge.svg)](https://github.com/django-mvp/django-mvp-layout/actions/workflows/tests.yml)
[![Build](https://github.com/django-mvp/django-mvp-layout/actions/workflows/build.yml/badge.svg)](https://github.com/django-mvp/django-mvp-layout/actions/workflows/build.yml)
[![Publish](https://github.com/django-mvp/django-mvp-layout/actions/workflows/publish.yml/badge.svg)](https://github.com/django-mvp/django-mvp-layout/actions/workflows/publish.yml)
[![codecov](https://codecov.io/gh/django-mvp/django-mvp-layout/branch/main/graph/badge.svg)](https://codecov.io/gh/django-mvp/django-mvp-layout)
[![PyPI](https://img.shields.io/pypi/v/django-mvp-layout)](https://pypi.org/project/django-mvp-layout/)
[![Python](https://img.shields.io/pypi/pyversions/django-mvp-layout)](https://pypi.org/project/django-mvp-layout/)
[![Django](https://img.shields.io/pypi/djversions/django-mvp-layout)](https://pypi.org/project/django-mvp-layout/)
[![License](https://img.shields.io/github/license/django-mvp/django-mvp-layout)](https://github.com/django-mvp/django-mvp-layout/blob/main/LICENSE)

Page layouts arranged by a nine-letter layout code, with sidebars that open, close, collapse and nest

## Scope & philosophy

The package arranges a header, two sidebars, a page and a footer, and makes the sidebars behave:
they open and close, shrink to an icon rail, become drawers on a narrow layout, and remember their
state. A layout is a page or a box inside one, and it nests inside itself. The package renders markup
and ships one stylesheet and one script. It has no models, views, URLs or settings, and it leaves the
look of everything inside the areas to the host project.

When two designs conflict, the one that keeps a layout accessible and its markup readable wins over
the one with more options.

## Installation

```bash
pip install django-mvp-layout
```

Then add it to `INSTALLED_APPS`, after `mvp`:

```python
INSTALLED_APPS = [
    # ...
    "mvp",
    "mvp_layout",
]
```

## Usage

A layout is written with Cotton components, or in a plain base template that the pages of your
project extend.

### With django-cotton

Load the stylesheet and script in the head, then write the layout:

```html
{% load static %}
<link rel="stylesheet" href="{% static 'mvp_layout/layout.css' %}" />
<script src="{% static 'mvp_layout/layout.js' %}"></script>

<c-layout view="lHh LpR lff">
  <c-layout.header><c-layout.toggle when="closed" /> My project</c-layout.header>
  <c-layout.sidebar label="Navigation">…</c-layout.sidebar>
  <c-layout.page tag="main">…</c-layout.page>
  <c-layout.footer>…</c-layout.footer>
</c-layout>
```

### In a plain template

1. Copy
   [`docs/examples/base.html`](https://github.com/django-mvp/django-mvp-layout/blob/main/docs/examples/base.html)
   to your project's `templates/base.html`, and add
   `django.template.context_processors.request` to your template settings.
2. Keep the three things the layout needs: `{% layout_attrs %}` on the root element,
   `{% sidebar_attrs %}` on each sidebar, and the stylesheet and script in the head:

   ```html
   {% load static mvp_layout %}
   <link rel="stylesheet" href="{% static 'mvp_layout/layout.css' %}" />
   <script src="{% static 'mvp_layout/layout.js' %}"></script>
   ```

3. Extend it in a page, filling the `header`, `navigation`, `content`, `aside` and `footer` blocks.

The nine-letter code in `{% layout_attrs "hHh LpR fFf" %}` places the areas. The
[developer guide](https://github.com/django-mvp/django-mvp-layout/tree/main/docs/developer)
covers the code, the components, both tags, styling, right-to-left pages and `MvpLayout`, the script a page of your
own uses to open and close sidebars.

## Contributing

Standards for this repository live in
[CONSTITUTION.md](https://github.com/django-mvp/django-mvp-layout/blob/main/CONSTITUTION.md),
and the vocabulary to use in issues and commits lives in
[CONTEXT.md](https://github.com/django-mvp/django-mvp-layout/blob/main/CONTEXT.md).

```bash
uv sync
uv run pytest
uv run pre-commit install
```

`demo/` is a Django project that shows the layouts in a browser while you work on this package,
with an overview, a playground, a nested-layouts page and a Without Cotton page:

```bash
uv run python manage.py runserver
```

## License

MIT. See [LICENSE](https://github.com/django-mvp/django-mvp-layout/blob/main/LICENSE).
