# AGENTS.md — Agent configuration for django-mvp-layout

Page layouts arranged by a nine-letter layout code, with sidebars that open, close, collapse and nest.

Presentation only: a set of Cotton components, two template tags, one stylesheet and one script. No
models, views, URLs, settings or migrations. It arranges the areas of a layout and draws nothing
inside them, which is the host project's job.

## Stack and commands

- **Stack:** Python 3.12+ / Django 5.2, 6.0 and 6.1, uv-managed (hatchling build backend), built on
  django-cotton. django-mvp is deliberately not a dependency
- **Install:** `uv sync`
- **Test (whole suite):** `uv run pytest -n auto --dist loadscope`
- **Test (one class or file, while iterating):** `uv run pytest <path> -x` —
  serial, because starting the workers costs more than a focused run takes
- **Lint:** `uv run pre-commit run --all-files`
- **Type-check:** `uv run mypy`
- **Build:** `uv build`
- **Demo project:** `uv run python manage.py runserver 0.0.0.0:8000`
- **Stylesheet:** `uv run python scripts/build_css.py` rewrites `mvp_layout/static/mvp_layout/layout.css`; never edit that file by hand
- **Demo stylesheet:** `npm install && npm run build:css` (Tailwind and daisyUI, demo only)
- **Bump the version:** `uv version` — never edit `pyproject.toml` alone, because `uv.lock`
  records this package's own version too

Lint is the pre-commit run rather than a bare `ruff check .`: the hook config
excludes `docs/` and migrations, so a raw invocation reports findings in paths
the gate does not cover, and they cannot be fixed without breaking the ones it
does.

`pre-commit run --all-files` only sees files git knows about. A new file that
has not been added is skipped, and the hooks then reformat it after the commit
that introduced it.

## The demo project

`demo/` is a Django project laid out by this package. It is how the package is
looked at while it is being written, and it is never deployed. Nothing in it is
distributed — `pyproject.toml` packages `mvp_layout` alone. It has no
database and no accounts.

`tests/settings.py` inherits `demo/settings.py` rather than restating it.

The pages are the overview, the playground (type a code, set the sidebars),
nested layouts (a card, a dialog, a layout in a layout) and Without Cotton. The
Without Cotton page extends `docs/examples/base.html` itself, because
`TEMPLATES["DIRS"]` includes `docs/examples/`, so the documented base template
is the one the browser tests run against.

**Adding a page** takes a view in `demo/views.py`, a route in `demo/urls.py`, a
template extending `demo/base.html`, and a link in that template's sidebar.

## Components

Components live at `mvp_layout/templates/cotton/layout/<name>.html`. Cotton
maps a tag's segments onto that path, so `<c-layout.sidebar>` resolves to
`cotton/layout/sidebar.html` and `<c-layout>` to `cotton/layout/index.html`.

The directory name is load-bearing and fails quietly: a component Cotton cannot
resolve renders as empty output rather than raising. `tests/test_smoke.py`
asserts the directory exists for that reason.

The components are built on the `layout_attrs` and `sidebar_attrs` template
tags, which are also the public surface for templates that don't use Cotton.
A change to the markup goes in both the component and
`docs/examples/base.html`.

## Browser tests

`tests/test_layout_js.py` runs the demo in chromium through pytest-playwright:
drawers, focus, inert regions, the cookie, container queries and nesting.
Anything that can be asserted on rendered HTML goes in the other modules
instead, which never skip.

## Releasing

Releases run through the shared release flow, never by hand and never by
pushing a tag.

1. Dispatch **Prepare Release** with a bump level. It opens a pull request
   carrying the version bump and the CHANGELOG section.
2. Merging that pull request is the release decision. **Tag Release** then cuts
   the tag and the GitHub Release from the merge commit.
3. **Publish** uploads to PyPI through trusted publishing. PyPI binds its
   trusted publisher to the `publish.yml` filename — renaming that file breaks
   publishing until the PyPI project settings are changed to match.

`pyproject.toml` holds the version and is the single source of truth for all
three steps.

**Tag Release skips a version with no matching CHANGELOG section**, which is
what stops the seed version being cut as a release. Leave it under
`## [Unreleased]` until Prepare Release promotes it: writing a `## [0.0.1]`
heading by hand makes the next push to `pyproject.toml` tag and release it.

Two things are needed before the first release: a PyPI trusted publisher for
this project pointed at `publish.yml`, and a `RELEASE_TOKEN` secret that can
write to this repository.

## Agent skills

### Issue tracker

Issues tracked in GitHub Issues via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`.
See `docs/agents/triage-labels.md`.

### Domain docs

One `CONTEXT.md` at the repository root and `docs/adr/` for decisions.
See `docs/agents/domain.md`.

### CI checks

CI runs from the shared reusable workflows in `django-mvp/shared`, pinned at
`v0.6.0`. Because they are called rather than inlined,
their status checks carry the calling job as a prefix. The required checks are:

- `call-build / Code Quality`
- `call-build / Security Scan`
- `call-build / Build Package`
- `call-tests / Test Python 3.12, Django 5.2`
- `call-tests / Test Python 3.12, Django 6.0`
- `call-tests / Test Python 3.13, Django 5.2`
- `call-tests / Test Python 3.13, Django 6.0`

`tests.yml` and `build.yml` deliberately carry no `paths:` filter on
`pull_request`. A required check that is filtered out never reports, and a
check that never reports blocks the merge.

## Working here

Standards and the quality bar live in `CONSTITUTION.md`. The vocabulary to use
in issues, commits and test names lives in `CONTEXT.md`. What the package is
trying to be good at lives in `GOALS.md`, and the order the work happens in
lives in `docs/ROADMAP.md`.
