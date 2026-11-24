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

This package requires [django-mvp](https://github.com/django-mvp/django-mvp).
It renders inside django-mvp's layout and reads its colours from the theme
django-mvp supplies, so it does nothing useful on its own.

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

`demo/` is a Django project on django-mvp's application shell, for looking at
this package in a browser while working on it:

```bash
uv run python manage.py migrate
uv run python manage.py seed_demo
uv run python manage.py runserver
```

## License

MIT. See [LICENSE](https://github.com/django-mvp/django-mvp-layout/blob/main/LICENSE).
