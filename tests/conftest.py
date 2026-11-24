"""Fixtures shared across the test suite."""

import os
from html.parser import HTMLParser

import pytest
from django import template as dj_template
from django.template import Context
from django.urls import reverse
from django_cotton.compiler_regex import CottonCompiler


class TagReader(HTMLParser):
    """Collects the attributes of the first start tag in a piece of HTML."""

    def __init__(self):
        super().__init__()
        self.attrs = None

    def handle_starttag(self, tag, attrs):
        if self.attrs is None:
            self.attrs = dict(attrs)


def attrs_of(html):
    """Return the attributes of the first tag in the HTML, by name."""
    reader = TagReader()
    reader.feed(html)
    return reader.attrs


class ElementReader(HTMLParser):
    """Collects every start tag in a piece of HTML, in order."""

    def __init__(self):
        super().__init__()
        self.found = []

    def handle_starttag(self, tag, attrs):
        self.found.append((tag, dict(attrs)))


def elements_of(html):
    """Return every start tag in the HTML as ``(name, attributes)``, in order."""
    reader = ElementReader()
    reader.feed(html)
    return reader.found


def with_data(html, prefix="data-mvpl"):
    """Return the elements of the HTML that carry a package data attribute.

    Ids are dropped and classes become sets, so two renderings of one layout
    compare equal whatever ids they were given and however their classes are
    spaced.
    """
    kept = []
    for tag, attrs in elements_of(html):
        if not any(name.startswith(prefix) for name in attrs):
            continue
        attrs = {name: value for name, value in attrs.items() if name != "id"}
        attrs["class"] = frozenset((attrs.get("class") or "").split())
        kept.append((tag, attrs))
    return kept


@pytest.fixture(scope="session")
def render():
    # No request is involved, which holds components to rendering anywhere a
    # template does, including outside the request cycle.
    compiler = CottonCompiler()

    def render_source(source, request=None, **context):
        template = dj_template.Template(compiler.process(source))
        return template.render(Context({"request": request, **context}))

    return render_source


@pytest.fixture
def overview_page(client, db):
    return client.get(reverse("overview")).content.decode()


@pytest.fixture(scope="session")
def chromium():
    # Locally a missing browser skips. In CI it fails, because a checks page
    # cannot tell a skipped test from a passing one.
    from playwright.sync_api import Error, sync_playwright

    try:
        with sync_playwright() as playwright:
            playwright.chromium.launch().close()
    except (Error, ImportError) as exc:  # pragma: no cover - environment probe
        unavailable = f"no chromium available to measure the page with: {exc}"
        if os.environ.get("CI"):
            pytest.fail(
                f"{unavailable}\n\nThe tests workflow installs chromium through "
                "the shared workflow's `install-playwright` input. Reaching this "
                "means that input was dropped or its install step did not run.",
                pytrace=False,
            )
        pytest.skip(unavailable)
