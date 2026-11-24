"""The layout's script and stylesheet in a real browser.

Only what a browser can measure belongs here: where each area lands, which
sidebars are drawers at a width, the host's rules against the package's, and
the mirrored layout under right-to-left. A check that works on rendered HTML
goes in the other modules, which cannot skip.
"""

from html.parser import HTMLParser

import pytest
from django.urls import reverse

PHONE = {"width": 390, "height": 800}
DESKTOP = {"width": 1440, "height": 900}

# Every test page that extends the documented base template, by route name.
BASE_PAGES = [
    "layouts-default",
    "layouts-contained",
    "layouts-nested",
    "layouts-narrow-box",
    "layouts-empty-aside",
    "layouts-outside-toggle",
    "layouts-rtl",
    "layouts-heavy",
    "layouts-host-rules",
    "layouts-host-colours",
]

pytestmark = pytest.mark.django_db


class AreaOrder(HTMLParser):
    """Collect the areas that are direct children of the base layout's grid."""

    AREAS = {
        "mvpl-header": "header",
        "mvpl-page": "page",
        "mvpl-footer": "footer",
    }
    VOID = {"meta", "link", "input", "br", "img", "hr"}

    def __init__(self) -> None:
        super().__init__()
        self.stack: list[tuple[str, dict[str, str | None]]] = []
        self.found: list[str] = []

    def handle_starttag(self, tag, attrs) -> None:
        attributes = dict(attrs)
        classes = (attributes.get("class") or "").split()
        in_grid = (
            len(self.stack) >= 2
            and "mvpl-grid" in (self.stack[-1][1].get("class") or "").split()
            and self.stack[-2][1].get("id") == "app"
        )
        if in_grid:
            for name, area in self.AREAS.items():
                if name in classes:
                    self.found.append(area)
            if "mvpl-sidebar" in classes:
                self.found.append(attributes["data-mvpl-side"] + " sidebar")
        if tag not in self.VOID:
            self.stack.append((tag, attributes))

    def handle_endtag(self, tag) -> None:
        if tag in self.VOID:
            return
        while self.stack:
            if self.stack.pop()[0] == tag:
                break


@pytest.fixture
def errors(page):
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
    def go(name, size=DESKTOP, query=""):
        page.set_viewport_size(size)
        page.goto(live_server.url + reverse(name) + query)
        page.wait_for_load_state()
        return page

    return go


class TestTheBaseTemplate:
    @pytest.mark.parametrize("name", BASE_PAGES)
    def test_each_page_extends_the_base_template(self, client, name) -> None:
        response = client.get(reverse(name))
        assert response.status_code == 200
        assert "examples/base.html" in [t.name for t in response.templates]

    @pytest.mark.parametrize("name", BASE_PAGES)
    def test_areas_are_in_the_order_a_reader_expects(self, client, name) -> None:
        parser = AreaOrder()
        parser.feed(client.get(reverse(name)).content.decode())
        assert parser.found == [
            "header",
            "left sidebar",
            "page",
            "right sidebar",
            "footer",
        ]

    @pytest.mark.parametrize("name", [*BASE_PAGES, "layouts-code"])
    @pytest.mark.parametrize("size", [PHONE, DESKTOP], ids=["phone", "desktop"])
    def test_each_page_loads_with_no_error_and_no_failed_request(
        self, visit, errors, name, size
    ) -> None:
        visit(name, size)
        assert errors == []
