# Set up a development environment

You need [uv](https://docs.astral.sh/uv/) and Git. uv installs the right Python for you.

## Get the code and its dependencies

```bash
git clone https://github.com/django-mvp/django-mvp-layout.git
cd django-mvp-layout
uv sync
uv run pre-commit install
```

`uv sync` installs the package with its development tools. `pre-commit install` runs the linters
on every commit.

## Run the demo project

The repository carries a demo project in `demo/`. It is not part of the package. It shows the
layouts in a browser while you change them, on four pages: an overview, a playground where you type
a layout code and set the sidebars, a page of nested layouts, and a page whose layout is written
without django-cotton.

```bash
uv run python manage.py runserver
```

Open <http://localhost:8000/>. The demo has no database and no accounts. The page reloads by itself
when you change a template or Python file.

The demo's own stylesheet is Tailwind and daisyUI, built into `demo/static/demo/demo.css`, which is
committed. After you change the classes a demo template uses, build it again. You need
[Node](https://nodejs.org/):

```bash
npm install
npm run build:css
```
