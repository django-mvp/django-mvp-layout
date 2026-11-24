"""Fixtures for the component tests that load a page in a browser."""

import pytest
from django.urls import reverse

PHONE = {"width": 390, "height": 800}
DESKTOP = {"width": 1440, "height": 900}


@pytest.fixture
def errors(page):
    """The script errors, console errors and failed requests a page raised."""
    found: list[str] = []
    page.on("pageerror", lambda exc: found.append(str(exc)))
    page.on("console", lambda m: found.append(m.text) if m.type == "error" else None)
    page.on("requestfailed", lambda r: found.append(f"failed: {r.url}"))
    page.on(
        "response",
        lambda r: found.append(f"{r.status}: {r.url}") if r.status >= 400 else None,
    )
    return found


@pytest.fixture
def visit(chromium, page, live_server, errors):
    """Open a component test page by route name at a window size."""

    def go(name, size=DESKTOP):
        page.set_viewport_size(size)
        page.goto(live_server.url + reverse(name))
        page.wait_for_load_state()
        return page

    return go
