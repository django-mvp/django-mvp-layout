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


def rect(page, selector):
    """Return the bounding box of the first match, in page coordinates."""
    return page.evaluate(
        """(selector) => {
          const r = document.querySelector(selector).getBoundingClientRect();
          return {left: r.left + scrollX, right: r.right + scrollX,
                  top: r.top + scrollY, bottom: r.bottom + scrollY,
                  width: r.width, height: r.height};
        }""",
        selector,
    )


def viewport_rect(page, selector):
    """Return the bounding box of the first match, relative to the window."""
    return page.evaluate(
        """(selector) => {
          const r = document.querySelector(selector).getBoundingClientRect();
          return {left: r.left, right: r.right, top: r.top, bottom: r.bottom,
                  width: r.width, height: r.height};
        }""",
        selector,
    )


def computed(page, selector, prop):
    return page.evaluate(
        "([s, p]) => getComputedStyle(document.querySelector(s))[p]", [selector, prop]
    )


def mode_of(page, selector):
    """Read the stylesheet's public signal for how a sidebar is drawn."""
    return page.evaluate(
        "(s) => getComputedStyle(document.querySelector(s))"
        ".getPropertyValue('--mvpl-mode').trim()",
        selector,
    )


def near(a, b, tolerance=1.5):
    return abs(a - b) <= tolerance


def settle(page, ms=400):
    # Sidebars animate their width and position.
    page.wait_for_timeout(ms)


def areas(page, root="#app"):
    return {
        "grid": rect(page, f"{root} > .mvpl-grid"),
        "header": rect(page, f"{root} > .mvpl-grid > .mvpl-header"),
        "left": rect(
            page, f'{root} > .mvpl-grid > .mvpl-sidebar[data-mvpl-side="left"]'
        ),
        "page": rect(page, f"{root} > .mvpl-grid > .mvpl-page"),
        "right": rect(
            page, f'{root} > .mvpl-grid > .mvpl-sidebar[data-mvpl-side="right"]'
        ),
        "footer": rect(page, f"{root} > .mvpl-grid > .mvpl-footer"),
    }


# Every choice for each of the four corners. The letter in a corner names the
# area that reaches it, and the middle row is always lpr.
CORNERS = [
    (top_left, top_right, bottom_left, bottom_right)
    for top_left in "hl"
    for top_right in "hr"
    for bottom_left in "fl"
    for bottom_right in "fr"
]


class TestPlacement:
    @pytest.mark.parametrize(
        ("top_left", "top_right", "bottom_left", "bottom_right"), CORNERS
    )
    def test_each_corner_is_taken_by_the_area_the_code_names(
        self, visit, top_left, top_right, bottom_left, bottom_right
    ) -> None:
        code = f"{top_left}h{top_right} lpr {bottom_left}f{bottom_right}"
        a = areas(visit("layouts-code", query=f"?view={code}".replace(" ", "%20")))
        grid = a["grid"]

        if top_left == "l":
            assert near(a["left"]["top"], grid["top"])
            assert near(a["header"]["left"], a["left"]["right"])
        else:
            assert near(a["header"]["left"], grid["left"])
            assert near(a["left"]["top"], a["header"]["bottom"])
        if top_right == "r":
            assert near(a["right"]["top"], grid["top"])
            assert near(a["header"]["right"], a["right"]["left"])
        else:
            assert near(a["header"]["right"], grid["right"])
            assert near(a["right"]["top"], a["header"]["bottom"])
        if bottom_left == "l":
            assert near(a["left"]["bottom"], grid["bottom"])
            assert near(a["footer"]["left"], a["left"]["right"])
        else:
            assert near(a["footer"]["left"], grid["left"])
            assert near(a["left"]["bottom"], a["footer"]["top"])
        if bottom_right == "r":
            assert near(a["right"]["bottom"], grid["bottom"])
            assert near(a["footer"]["right"], a["right"]["left"])
        else:
            assert near(a["footer"]["right"], grid["right"])
            assert near(a["right"]["bottom"], a["footer"]["top"])

    def test_an_upper_case_area_stays_in_place_while_the_layout_scrolls(
        self, visit
    ) -> None:
        page = visit("layouts-code", query="?view=hHh%20LpR%20fFf&tall=1")
        parts = {
            "header": "#app > .mvpl-grid > .mvpl-header",
            "left": '#app > .mvpl-grid > [data-mvpl-side="left"] > .mvpl-panel',
            "right": '#app > .mvpl-grid > [data-mvpl-side="right"] > .mvpl-panel',
            "footer": "#app > .mvpl-grid > .mvpl-footer",
        }
        before = {name: viewport_rect(page, s) for name, s in parts.items()}
        page.evaluate("window.scrollTo(0, 600)")
        settle(page, 150)
        assert page.evaluate("window.scrollY") > 0
        after = {name: viewport_rect(page, s) for name, s in parts.items()}
        for name in ("header", "left", "right"):
            assert near(after[name]["top"], before[name]["top"]), name
        assert near(after["footer"]["bottom"], page.evaluate("innerHeight"))

    def test_a_lower_case_area_scrolls_away_with_the_layout(self, visit) -> None:
        page = visit("layouts-code", query="?view=hhh%20lpr%20fff&tall=1")
        header = "#app > .mvpl-grid > .mvpl-header"
        page.evaluate("window.scrollTo(0, 600)")
        settle(page, 150)
        assert viewport_rect(page, header)["bottom"] < 0

    def test_a_contained_layout_fills_its_box_and_scrolls_inside_it(
        self, visit
    ) -> None:
        page = visit("layouts-contained")
        box = viewport_rect(page, "#contained-box")
        layout = viewport_rect(page, "#contained")
        assert near(layout["width"], box["width"])
        assert near(layout["height"], box["height"])

        page.mouse.move(box["left"] + box["width"] / 2, box["top"] + box["height"] / 2)
        page.mouse.wheel(0, 300)
        page.wait_for_function(
            "document.querySelector('#contained > .mvpl-grid').scrollTop > 0"
        )
        assert page.evaluate("window.scrollY") == 0

    def test_nested_layouts_each_place_their_own_areas(self, visit) -> None:
        page = visit("layouts-nested")
        outer = areas(page, "#outer")
        inner = areas(page, "#inner")
        for layout in (outer, inner):
            assert layout["header"]["bottom"] <= layout["page"]["top"] + 1.5
            assert layout["left"]["right"] <= layout["page"]["left"] + 1.5
            assert layout["page"]["right"] <= layout["right"]["left"] + 1.5
            assert layout["header"]["bottom"] <= layout["footer"]["top"] + 1.5
        # lHh puts the inner layout's left sidebar at the top-left corner, which
        # hHh gives to the header of the outer one.
        assert near(inner["left"]["top"], inner["grid"]["top"])
        assert near(outer["header"]["top"], outer["grid"]["top"])
        # The inner layout is drawn inside the outer layout's page.
        assert inner["grid"]["left"] >= outer["page"]["left"] - 1.5
        assert inner["grid"]["right"] <= outer["page"]["right"] + 1.5

    def test_a_sidebar_is_a_drawer_in_a_narrow_box_on_a_wide_window(
        self, visit
    ) -> None:
        page = visit("layouts-narrow-box")
        assert page.evaluate("innerWidth") >= 1400
        shell = '#app > .mvpl-grid > [data-mvpl-side="left"]'
        boxed = '#narrow > .mvpl-grid > [data-mvpl-side="left"]'
        assert mode_of(page, shell) == "docked"
        assert mode_of(page, boxed) == "overlay"

    def test_an_empty_panel_takes_no_space(self, visit) -> None:
        right = '#app > .mvpl-grid > [data-mvpl-side="right"]'
        assert rect(visit("layouts-default"), right)["width"] > 0
        page = visit("layouts-empty-aside")
        assert rect(page, right)["width"] == 0
        assert near(areas(page)["page"]["right"], areas(page)["grid"]["right"])


class TestTheHostsRules:
    def test_rules_on_bare_aside_and_header_still_apply_outside_a_layout(
        self, visit
    ) -> None:
        page = visit("layouts-host-rules")
        assert computed(page, "#plain-aside", "marginTop") == "11px"
        assert computed(page, "#plain-header", "marginTop") == "12px"

    def test_the_stylesheet_styles_nothing_but_its_own_elements(self, visit) -> None:
        page = visit("layouts-host-rules")
        differences = page.evaluate(
            """() => {
              const read = (el) => Object.fromEntries(
                [...getComputedStyle(el)].filter((p) => !p.startsWith('--'))
                  .map((p) => [p, getComputedStyle(el).getPropertyValue(p)]));
              const plain = ['#plain-aside', '#plain-header']
                .map((s) => document.querySelector(s));
              const withSheet = plain.map(read);
              const sheet = [...document.styleSheets]
                .find((s) => s.href && s.href.endsWith('layout.css'));
              sheet.disabled = true;
              const without = plain.map(read);
              // The size of an element follows the width of the page it is in,
              // and the stylesheet decides that, so sizes are left out.
              const sized = /^(inline-size|block-size|width|height|.*-origin)$/;
              return withSheet.flatMap((now, i) => Object.keys(now)
                .filter((p) => !sized.test(p) && now[p] !== without[i][p]));
            }"""
        )
        assert differences == []

    def test_a_rule_on_the_sidebar_class_and_one_on_its_closed_state_take_effect(
        self, visit, page
    ) -> None:
        # The left sidebar is remembered as closed, the right is open.
        page.context.add_cookies(
            [{"name": "mvpl-nav", "value": "closed", "url": "http://localhost"}]
        )
        page = visit("layouts-host-rules")
        left = '#app > .mvpl-grid > [data-mvpl-side="left"]'
        right = '#app > .mvpl-grid > [data-mvpl-side="right"]'
        assert page.locator(left).get_attribute("data-mvpl-state") == "closed"
        assert computed(page, left, "backgroundColor") == "rgb(4, 5, 6)"
        assert computed(page, right, "backgroundColor") == "rgb(1, 2, 3)"

    def test_a_host_colour_variable_colours_the_sidebar(self, visit) -> None:
        page = visit("layouts-host-colours")
        left = '#app > .mvpl-grid > [data-mvpl-side="left"]'
        assert computed(page, left, "backgroundColor") == "rgb(10, 20, 30)"

    def test_without_a_theme_the_sidebar_follows_the_system_colours(
        self, visit
    ) -> None:
        page = visit("layouts-default")
        left = '#app > .mvpl-grid > [data-mvpl-side="left"]'
        light = computed(page, left, "backgroundColor")
        page.evaluate("document.documentElement.style.colorScheme = 'dark'")
        assert computed(page, left, "backgroundColor") != light


class TestRightToLeft:
    @pytest.mark.parametrize("size", [DESKTOP, PHONE], ids=["desktop", "phone"])
    def test_the_left_sidebar_is_at_the_reading_start_side_which_is_the_right(
        self, visit, size
    ) -> None:
        page = visit("layouts-rtl", size)
        assert page.evaluate("document.documentElement.dir") == "rtl"
        grid = "#app > .mvpl-grid"
        left = f'{grid} > [data-mvpl-side="left"]'
        panel = f"{left} > .mvpl-panel"
        width = page.evaluate("innerWidth")
        if size is DESKTOP:
            page_area = viewport_rect(page, f"{grid} > .mvpl-page")
            assert viewport_rect(page, left)["left"] >= page_area["right"] - 1.5
            assert near(viewport_rect(page, panel)["right"], width, 20)
        else:
            # A drawer waits off the right edge and slides in from it.
            assert viewport_rect(page, panel)["left"] >= width - 1
            page.locator(f"{grid} > .mvpl-header [data-mvpl-toggle='left']").click()
            settle(page)
            opened = viewport_rect(page, panel)
            assert opened["left"] < width - 100
            assert near(opened["right"], width, 20)
