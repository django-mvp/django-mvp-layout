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
    "layouts-toggles",
    "layouts-sidebars",
    "layouts-behaviors",
    "layouts-focus",
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


LEFT = '#app > .mvpl-grid > [data-mvpl-side="left"]'
RIGHT = '#app > .mvpl-grid > [data-mvpl-side="right"]'


def state_of(page, selector):
    """Read the attribute a sidebar's open or closed state is kept in."""
    return page.locator(selector).get_attribute("data-mvpl-state")


def width_of(page, selector):
    """Read a sidebar's drawn width once its transition has finished."""
    settle(page)
    return rect(page, selector)["width"]


def length_of(page, selector, variable):
    """Resolve a length variable on an element to pixels, the way the browser does."""
    return page.evaluate(
        """([selector, variable]) => {
          const el = document.querySelector(selector);
          const probe = document.createElement("div");
          probe.style.cssText = `position: absolute; width: var(${variable})`;
          el.appendChild(probe);
          const width = probe.getBoundingClientRect().width;
          probe.remove();
          return width;
        }""",
        [selector, variable],
    )


class TestToggles:
    def test_a_toggle_closes_and_opens_a_docked_sidebar(self, visit) -> None:
        page = visit("layouts-toggles")
        assert mode_of(page, LEFT) == "docked"
        assert state_of(page, LEFT) == "open"
        opened = width_of(page, LEFT)
        assert opened > 0

        page.locator("#toggle").click()
        assert state_of(page, LEFT) == "closed"
        assert width_of(page, LEFT) == 0
        assert page.locator("#toggle").get_attribute("aria-expanded") == "false"

        page.locator("#toggle").click()
        assert state_of(page, LEFT) == "open"
        assert near(width_of(page, LEFT), opened)
        assert page.locator("#toggle").get_attribute("aria-expanded") == "true"

    def test_a_toggle_names_the_sidebar_it_controls(self, visit) -> None:
        page = visit("layouts-toggles")
        sidebar_id = page.locator(LEFT).get_attribute("id")
        assert sidebar_id
        assert page.locator("#toggle").get_attribute("aria-controls") == sidebar_id
        assert page.locator("#aside-toggle").get_attribute(
            "aria-controls"
        ) == page.locator(RIGHT).get_attribute("id")

    def test_a_toggle_for_one_state_shows_only_in_that_state(self, visit) -> None:
        page = visit("layouts-toggles")
        assert page.locator("#show-only-open").is_visible()
        assert not page.locator("#show-only-closed").is_visible()

        page.locator("#show-only-open").click()
        assert state_of(page, LEFT) == "closed"
        assert page.locator("#show-only-closed").is_visible()
        assert not page.locator("#show-only-open").is_visible()

        page.locator("#show-only-closed").click()
        assert state_of(page, LEFT) == "open"
        assert page.locator("#show-only-open").is_visible()

    def test_a_toggle_outside_its_layout_controls_the_layout_it_names(
        self, visit
    ) -> None:
        page = visit("layouts-outside-toggle")
        boxed = '#boxed > .mvpl-grid > [data-mvpl-side="left"]'
        # The box is narrower than the sidebar's breakpoint, so it is a drawer.
        assert mode_of(page, boxed) == "overlay"
        page.locator("#outside").click()
        assert page.locator(boxed).get_attribute("data-mvpl-overlay") == "open"
        assert page.locator(LEFT).get_attribute("data-mvpl-overlay") is None
        assert state_of(page, LEFT) == "open"
        assert page.locator("#outside").get_attribute("aria-controls") == (
            page.locator(boxed).get_attribute("id")
        )

    def test_a_toggle_in_a_nested_layout_acts_only_on_its_own_layout(
        self, visit
    ) -> None:
        page = visit("layouts-nested")
        outer = '#outer > .mvpl-grid > [data-mvpl-side="left"]'
        inner = '#inner > .mvpl-grid > [data-mvpl-side="left"]'
        assert mode_of(page, outer) == mode_of(page, inner) == "docked"
        for toggle, sidebar in (("#outer-toggle", outer), ("#inner-toggle", inner)):
            assert page.locator(toggle).get_attribute("aria-controls") == (
                page.locator(sidebar).get_attribute("id")
            )

        page.locator("#inner-toggle").click()
        assert state_of(page, inner) == "closed"
        assert state_of(page, outer) == "open"

        page.locator("#outer-toggle").click()
        assert state_of(page, outer) == "closed"
        assert state_of(page, inner) == "closed"
        page.locator("#inner-toggle").click()
        assert state_of(page, inner) == "open"
        assert state_of(page, outer) == "closed"

    def test_a_sidebar_that_never_closes_offers_no_toggle_beside_the_page(
        self, visit
    ) -> None:
        page = visit("layouts-sidebars")
        pinned = '#sidebars > .mvpl-grid > [data-mvpl-side="right"]'
        assert mode_of(page, pinned) == "docked"
        assert page.locator("#pinned-toggle").is_hidden()
        assert state_of(page, pinned) == "open"
        assert width_of(page, pinned) > 0

    def test_a_sidebar_with_an_empty_panel_hides_every_toggle_for_it(
        self, visit
    ) -> None:
        page = visit("layouts-empty-aside")
        assert page.locator("[data-mvpl-toggle='right']").is_hidden()
        assert page.locator("[data-mvpl-toggle='left']").is_visible()


class TestIconRail:
    RAIL = '#sidebars > .mvpl-grid > [data-mvpl-side="left"]'

    def test_an_open_sidebar_is_not_a_rail(self, visit) -> None:
        page = visit("layouts-sidebars")
        assert page.locator(self.RAIL).get_attribute("data-mvpl-rail") is None
        assert page.locator("#rail-hide").is_visible()
        assert not page.locator("#rail-only").is_visible()

    def test_closing_leaves_the_sidebar_beside_the_page_at_its_rail_width(
        self, visit
    ) -> None:
        page = visit("layouts-sidebars")
        assert mode_of(page, self.RAIL) == "docked"
        page.locator("#rail-toggle").click()
        assert state_of(page, self.RAIL) == "closed"
        assert page.locator(self.RAIL).get_attribute("data-mvpl-rail") is not None
        rail = length_of(page, self.RAIL, "--mvpl-rail-w")
        assert rail > 0
        assert near(width_of(page, self.RAIL), rail)
        assert near(
            rect(page, "#sidebars > .mvpl-grid > .mvpl-page")["left"],
            rect(page, self.RAIL)["right"],
        )

    def test_a_rail_shows_what_is_for_it_and_hides_what_is_not(self, visit) -> None:
        page = visit("layouts-sidebars")
        page.locator("#rail-toggle").click()
        settle(page)
        assert page.locator("#rail-only").is_visible()
        assert not page.locator("#rail-hide").is_visible()
        assert computed(page, "#rail-hide", "display") == "none"

        page.locator("#rail-toggle").click()
        settle(page)
        assert page.locator("#rail-hide").is_visible()
        assert not page.locator("#rail-only").is_visible()


def drawer_open(page, selector):
    """Report whether a sidebar is open as a drawer."""
    return page.locator(selector).get_attribute("data-mvpl-overlay") == "open"


def focus_is_in(page, selector):
    """Report whether the focused element is inside the one the selector names."""
    return page.evaluate(
        "(s) => document.querySelector(s).contains(document.activeElement)", selector
    )


class TestDrawers:
    PANEL = f"{LEFT} > .mvpl-panel"

    def test_a_toggle_opens_the_sidebar_as_a_modal_dialog(self, visit) -> None:
        page = visit("layouts-toggles", PHONE)
        assert mode_of(page, LEFT) == "overlay"
        assert page.locator(self.PANEL).get_attribute("role") is None

        page.locator("#toggle").click()
        assert drawer_open(page, LEFT)
        assert page.locator(self.PANEL).get_attribute("role") == "dialog"
        assert page.locator(self.PANEL).get_attribute("aria-modal") == "true"
        assert page.locator("#toggle").get_attribute("aria-expanded") == "true"
        # A drawer is not the docked state, which stays what the reader left.
        assert state_of(page, LEFT) == "open"

    def test_focus_moves_into_the_drawer_and_the_other_areas_are_inert(
        self, visit
    ) -> None:
        page = visit("layouts-toggles", PHONE)
        page.locator("#toggle").click()
        assert focus_is_in(page, self.PANEL)
        areas_inert = page.evaluate(
            """() => Object.fromEntries(
              [...document.querySelectorAll("#app > .mvpl-grid > *")]
                .map((el) => [el.dataset.mvplSide ?? el.className, el.inert]))"""
        )
        assert areas_inert == {
            "mvpl-header": True,
            "left": False,
            "mvpl-page": True,
            "right": True,
            "mvpl-footer": True,
        }

    def test_escape_closes_it_and_focus_returns_to_the_toggle(self, visit) -> None:
        page = visit("layouts-toggles", PHONE)
        page.locator("#toggle").click()
        page.keyboard.press("Escape")
        assert not drawer_open(page, LEFT)
        assert page.evaluate("document.activeElement.id") == "toggle"
        assert page.locator(self.PANEL).get_attribute("role") is None

    def test_the_backdrop_closes_it_and_focus_returns(self, visit) -> None:
        page = visit("layouts-toggles", PHONE)
        page.locator("#toggle").click()
        backdrop = viewport_rect(page, f"{LEFT} > .mvpl-backdrop")
        panel = viewport_rect(page, self.PANEL)
        assert panel["right"] < backdrop["right"] - 4
        page.mouse.click(
            backdrop["right"] - 2, backdrop["top"] + backdrop["height"] / 2
        )
        assert not drawer_open(page, LEFT)
        assert page.evaluate("document.activeElement.id") == "toggle"

    def test_following_a_link_inside_it_closes_it(self, visit) -> None:
        page = visit("layouts-toggles", PHONE)
        page.locator("#toggle").click()
        page.locator("#link").click()
        assert not drawer_open(page, LEFT)
        assert page.evaluate("document.querySelectorAll('[inert]').length") == 0

    def test_a_whole_page_drawer_locks_the_page_while_it_is_open(self, visit) -> None:
        page = visit("layouts-toggles", PHONE)
        root = "document.documentElement.classList.contains('mvpl-locked')"
        assert not page.evaluate(root)
        page.locator("#toggle").click()
        assert page.evaluate(root)
        page.keyboard.press("Escape")
        assert not page.evaluate(root)

    def test_a_contained_drawer_leaves_the_page_unlocked(self, visit) -> None:
        page = visit("layouts-contained", PHONE)
        page.locator("#contained [data-mvpl-toggle='left']").click()
        drawer = '#contained > .mvpl-grid > [data-mvpl-side="left"]'
        assert drawer_open(page, drawer)
        assert not page.evaluate(
            "document.documentElement.classList.contains('mvpl-locked')"
        )

    def test_resizing_across_the_breakpoint_closes_it_and_frees_the_page(
        self, visit
    ) -> None:
        page = visit("layouts-toggles", PHONE)
        page.locator("#toggle").click()
        assert drawer_open(page, LEFT)

        page.set_viewport_size(DESKTOP)
        settle(page)
        assert mode_of(page, LEFT) == "docked"
        assert not drawer_open(page, LEFT)
        assert page.evaluate("document.querySelectorAll('[inert]').length") == 0
        assert not page.evaluate(
            "document.documentElement.classList.contains('mvpl-locked')"
        )

    def test_a_sidebar_set_to_overlay_is_a_drawer_at_desktop_width(self, visit) -> None:
        page = visit("layouts-behaviors", DESKTOP)
        left = '#modes > .mvpl-grid > [data-mvpl-side="left"]'
        assert page.evaluate("innerWidth") >= 1400
        assert mode_of(page, left) == "overlay"

        page.locator("#overlay-toggle").click()
        assert drawer_open(page, left)
        assert page.locator(f"{left} > .mvpl-panel").get_attribute("role") == "dialog"
        assert page.locator(f"{left} > .mvpl-panel").get_attribute("aria-modal") == (
            "true"
        )
        assert state_of(page, left) == "open"

    def test_a_sidebar_set_to_docked_stays_beside_the_page_at_phone_width(
        self, visit
    ) -> None:
        page = visit("layouts-behaviors", PHONE)
        right = '#modes > .mvpl-grid > [data-mvpl-side="right"]'
        assert mode_of(page, right) == "docked"
        opened = width_of(page, right)
        assert opened > 0

        page.locator("#docked-toggle").click()
        assert state_of(page, right) == "closed"
        assert not drawer_open(page, right)
        assert width_of(page, right) < opened


class TestDrawerFocus:
    OUTER = '#app > .mvpl-grid > [data-mvpl-side="left"] > .mvpl-panel'
    INNER = '#inner > .mvpl-grid > [data-mvpl-side="left"] > .mvpl-panel'

    @pytest.mark.parametrize(
        ("toggle", "panel", "size"),
        [
            ("#toggle", OUTER, PHONE),
            ("#inner-toggle", INNER, DESKTOP),
        ],
        ids=["whole-page", "contained"],
    )
    @pytest.mark.parametrize("key", ["Tab", "Shift+Tab"])
    def test_tab_never_leaves_an_open_drawer(
        self, visit, toggle, panel, size, key
    ) -> None:
        page = visit("layouts-focus", size)
        page.locator(toggle).click()
        count = page.locator(f"{panel} :is(a, button)").count()
        assert count == 3
        for _ in range(count + 2):
            page.keyboard.press(key)
            assert focus_is_in(page, panel)

    def test_tab_wraps_from_the_last_element_to_the_first(self, visit) -> None:
        page = visit("layouts-focus", DESKTOP)
        page.locator("#inner-toggle").click()
        links = f"{TestDrawerFocus.INNER} :is(a, button)"
        page.locator(links).last.focus()
        page.keyboard.press("Tab")
        assert page.evaluate(
            "(s) => document.activeElement === document.querySelector(s)", links
        )
        page.keyboard.press("Shift+Tab")
        assert page.evaluate(
            "(s) => document.activeElement === [...document.querySelectorAll(s)].at(-1)",
            links,
        )

    def test_focus_outside_an_open_drawer_is_pulled_back_in(self, visit) -> None:
        page = visit("layouts-focus", DESKTOP)
        page.locator("#inner-toggle").click()
        page.evaluate("document.querySelector('#after').focus()")
        page.keyboard.press("Tab")
        assert focus_is_in(page, self.INNER)

    def test_escape_closes_only_the_topmost_of_nested_drawers(self, visit) -> None:
        page = visit("layouts-nested", DESKTOP)
        outer = '#outer > .mvpl-grid > [data-mvpl-side="left"]'
        inner = '#inner > .mvpl-grid > [data-mvpl-side="left"]'
        # Both boxes narrower than the sidebars' breakpoint, so both are drawers.
        page.evaluate(
            "document.querySelector('#outer-box').style.width = '560px';"
            "document.querySelector('#inner-box').style.width = '500px'"
        )
        settle(page)
        assert mode_of(page, outer) == mode_of(page, inner) == "overlay"
        page.locator("#inner-toggle").click()
        page.locator("#outer-toggle").click()
        assert drawer_open(page, outer) and drawer_open(page, inner)

        # The drawer opened last is the topmost.
        page.keyboard.press("Escape")
        assert drawer_open(page, inner) and not drawer_open(page, outer)
        page.keyboard.press("Escape")
        assert not drawer_open(page, inner)


class SidebarStates(HTMLParser):
    """Collect each sidebar's side and drawn state, in document order."""

    def __init__(self) -> None:
        super().__init__()
        self.found: list[tuple[str | None, str | None]] = []

    def handle_starttag(self, tag, attrs) -> None:
        attributes = dict(attrs)
        if "mvpl-sidebar" in (attributes.get("class") or "").split():
            self.found.append(
                (attributes.get("data-mvpl-side"), attributes.get("data-mvpl-state"))
            )


def drawn_states(response):
    """Return the (side, state) pair of every sidebar in a response."""
    parser = SidebarStates()
    parser.feed(response.content.decode())
    return parser.found


# Records what the sidebar looks like at DOMContentLoaded and on each of the
# first frames, before anything the layout script does after loading can show.
RECORD_FRAMES = """
window.mvplFrames = [];
const sample = () => {
  const sb = document.querySelector('#app > .mvpl-grid > [data-mvpl-side="left"]');
  if (!sb) return;
  window.mvplFrames.push({
    state: sb.getAttribute("data-mvpl-state"),
    width: sb.getBoundingClientRect().width,
  });
};
document.addEventListener("DOMContentLoaded", sample);
let frames = 0;
const tick = () => {
  sample();
  if (++frames < 20) requestAnimationFrame(tick);
};
requestAnimationFrame(tick);
"""


def remembered(page):
    """Return the layout cookies the browser holds, by name."""
    return {
        cookie["name"]: cookie["value"]
        for cookie in page.context.cookies()
        if cookie["name"].startswith("mvpl-")
    }


def remember_in_browser(page, name, value):
    """Give the browser a layout cookie before the page is visited."""
    page.context.add_cookies(
        [{"name": name, "value": value, "url": "http://localhost"}]
    )


class TestRememberedState:
    def test_the_server_draws_a_remembered_closed_sidebar_closed(self, client) -> None:
        client.cookies["mvpl-nav"] = "closed"
        assert drawn_states(client.get(reverse("layouts-toggles"))) == [
            ("left", "closed"),
            ("right", "open"),
        ]

    def test_without_a_cookie_the_sidebar_is_in_its_options_state(self, client) -> None:
        assert drawn_states(client.get(reverse("layouts-toggles"))) == [
            ("left", "open"),
            ("right", "open"),
        ]

    def test_a_value_that_is_neither_open_nor_closed_is_ignored(self, client) -> None:
        client.cookies["mvpl-nav"] = "ajar"
        assert drawn_states(client.get(reverse("layouts-toggles")))[0] == (
            "left",
            "open",
        )

    def test_the_server_ignores_a_cookie_on_a_sidebar_that_never_closes(
        self, client
    ) -> None:
        client.cookies["mvpl-pinned"] = "closed"
        # The page's own boxed layout comes first, then the base layout's
        # right sidebar after the page content.
        states = drawn_states(client.get(reverse("layouts-sidebars")))
        assert states == [
            ("left", "open"),
            ("left", "open"),
            ("right", "open"),
            ("right", "open"),
        ]

    @pytest.mark.parametrize("name", ["layouts-toggles", "layouts-default"])
    def test_sidebars_sharing_a_name_share_the_one_cookie(self, client, name) -> None:
        client.cookies["mvpl-nav"] = "closed"
        assert drawn_states(client.get(reverse(name)))[0] == ("left", "closed")

    def test_closing_writes_the_cookie_and_opening_again_updates_it(
        self, visit
    ) -> None:
        page = visit("layouts-toggles")
        assert remembered(page) == {}
        page.locator("#toggle").click()
        assert remembered(page) == {"mvpl-nav": "closed"}
        page.locator("#toggle").click()
        assert remembered(page) == {"mvpl-nav": "open"}

    def test_a_reload_draws_it_closed_from_the_first_frame(self, visit) -> None:
        page = visit("layouts-toggles")
        page.locator("#toggle").click()
        page.add_init_script(RECORD_FRAMES)
        page.reload()
        page.wait_for_function("window.mvplFrames.length >= 5")
        frames = page.evaluate("window.mvplFrames")
        assert {frame["state"] for frame in frames} == {"closed"}
        assert {frame["width"] for frame in frames} == {0}

    def test_a_sidebar_with_no_name_writes_no_cookie_and_reopens_on_reload(
        self, visit
    ) -> None:
        page = visit("layouts-sidebars")
        rail = '#sidebars > .mvpl-grid > [data-mvpl-side="left"]'
        page.locator("#rail-toggle").click()
        assert state_of(page, rail) == "closed"
        assert remembered(page) == {}
        page.reload()
        assert state_of(page, rail) == "open"

    def test_two_sidebars_with_one_name_share_the_state_across_pages(
        self, visit
    ) -> None:
        page = visit("layouts-toggles")
        page.locator("#toggle").click()
        other = visit("layouts-default")
        assert state_of(other, LEFT) == "closed"
        assert remembered(other) == {"mvpl-nav": "closed"}

    def test_a_cookie_that_is_neither_open_nor_closed_is_ignored(
        self, visit, page
    ) -> None:
        remember_in_browser(page, "mvpl-nav", "ajar")
        assert state_of(visit("layouts-toggles"), LEFT) == "open"

    def test_a_cookie_on_a_sidebar_that_never_closes_is_ignored(
        self, visit, page
    ) -> None:
        remember_in_browser(page, "mvpl-pinned", "closed")
        page = visit("layouts-sidebars")
        pinned = '#sidebars > .mvpl-grid > [data-mvpl-side="right"]'
        assert state_of(page, pinned) == "open"
        assert width_of(page, pinned) > 0
