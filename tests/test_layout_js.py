"""The layout's script and stylesheet in a real browser.

Only what a browser can measure belongs here: which sidebars are drawers at a
width, focus, inert regions, the cookie, container queries and nesting. A check
that works on rendered HTML goes in the other modules, which cannot skip.
"""

import pytest
from django.urls import reverse

PHONE = {"width": 390, "height": 800}
DESKTOP = {"width": 1440, "height": 900}

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("chromium")]


@pytest.fixture
def errors(page):
    found: list[str] = []
    page.on("pageerror", lambda exc: found.append(str(exc)))
    page.on("console", lambda m: found.append(m.text) if m.type == "error" else None)
    return found


@pytest.fixture
def visit(page, live_server, errors):
    def go(name, size=DESKTOP, query=""):
        page.set_viewport_size(size)
        page.goto(live_server.url + reverse(name) + query)
        page.wait_for_load_state()
        return page

    return go


def state(page, layout_id):
    return page.evaluate(f"MvpLayout.state(document.getElementById('{layout_id}'))")


def box(page, layout_id, side):
    return page.evaluate(
        """([id, side]) => {
          const sb = document.querySelector(`#${id} > .mvpl-grid > .mvpl-sidebar[data-side="${side}"]`);
          const panel = sb.querySelector(':scope > .mvpl-panel');
          const r = sb.getBoundingClientRect(), p = panel.getBoundingClientRect();
          return {w: r.width, left: p.left, right: p.right,
                  rail: sb.hasAttribute('data-mvpl-rail'), role: panel.getAttribute('role')};
        }""",
        [layout_id, side],
    )


def settle(page, ms=350):
    # Sidebars animate their width and position.
    page.wait_for_timeout(ms)


def locked(page):
    return page.evaluate("document.documentElement.classList.contains('mvpl-locked')")


def overflow(page):
    return page.evaluate("document.documentElement.scrollWidth - window.innerWidth")


class TestEveryPage:
    @pytest.mark.parametrize("name", ["home", "playground", "nested", "plain"])
    @pytest.mark.parametrize("size", [PHONE, DESKTOP], ids=["phone", "desktop"])
    def test_loads_cleanly_and_never_scrolls_sideways(
        self, visit, errors, name, size
    ) -> None:
        page = visit(name, size)
        assert errors == []
        assert overflow(page) <= 0


class TestTheShellAtDesktopWidth:
    def test_both_sidebars_sit_beside_the_page(self, visit) -> None:
        s = state(visit("home"), "demo")
        assert s["left"]["mode"] == "docked" and s["left"]["visible"]
        assert s["right"]["mode"] == "docked" and s["right"]["visible"]

    def test_the_icon_sidebar_closes_to_a_rail_and_reopens(self, visit) -> None:
        page = visit("home")
        page.locator('#demo .mvpl-sidebar[data-side="left"] [data-mvpl-toggle]').click()
        settle(page)
        closed = box(page, "demo", "left")
        assert closed["rail"] and closed["w"] < 80
        labels = page.evaluate(
            "[...document.querySelectorAll('#demo .mvpl-sidebar[data-side=left] .mvpl-rail-hide')]"
            ".some(el => el.checkVisibility())"
        )
        assert not labels
        page.locator('#demo .mvpl-sidebar[data-side="left"] [data-mvpl-toggle]').click()
        settle(page)
        assert box(page, "demo", "left")["w"] > 200

    def test_a_closed_sidebar_stays_closed_across_a_reload(self, visit) -> None:
        page = visit("home")
        page.locator(
            '#demo > .mvpl-grid > .mvpl-header [data-mvpl-toggle="right"]'
        ).click()
        settle(page)
        assert box(page, "demo", "right")["w"] < 1
        page.reload()
        # Drawn closed by the server from the cookie, so no animation to wait for.
        assert box(page, "demo", "right")["w"] < 1
        assert (
            page.locator('#demo .mvpl-sidebar[data-side="right"]').get_attribute(
                "data-state"
            )
            == "closed"
        )

    def test_the_fixed_header_and_sidebar_stay_while_the_page_scrolls(
        self, visit
    ) -> None:
        page = visit("nested")
        page.evaluate("window.scrollTo(0, 800)")
        settle(page, 150)
        header = page.evaluate(
            "document.querySelector('#demo > .mvpl-grid > .mvpl-header').getBoundingClientRect().top"
        )
        panel = page.evaluate(
            "document.querySelector('#demo > .mvpl-grid > .mvpl-sidebar[data-side=left] > .mvpl-panel')"
            ".getBoundingClientRect().top"
        )
        assert abs(header) < 1
        assert abs(panel) < 1

    def test_a_page_with_an_empty_sidebar_has_none_and_no_toggle_for_it(
        self, visit
    ) -> None:
        page = visit("nested")
        assert not state(page, "demo")["right"]["present"]
        assert not page.locator(
            '#demo > .mvpl-grid > .mvpl-header [data-mvpl-toggle="right"]'
        ).is_visible()


class TestTheShellAtPhoneWidth:
    def test_both_sidebars_are_closed_drawers(self, visit) -> None:
        s = state(visit("home", PHONE), "demo")
        assert s["left"]["mode"] == "overlay" and not s["left"]["visible"]
        assert s["right"]["mode"] == "overlay" and not s["right"]["visible"]

    def test_a_drawer_is_a_modal_dialog(self, visit) -> None:
        page = visit("home", PHONE)
        toggle = page.locator(
            '#demo > .mvpl-grid > .mvpl-header [data-mvpl-toggle="left"]'
        )
        toggle.click()
        settle(page)
        opened = box(page, "demo", "left")
        assert opened["left"] >= -1 and opened["role"] == "dialog"
        assert page.evaluate(
            "!!document.activeElement.closest('#demo .mvpl-sidebar[data-side=left]')"
        )
        assert page.evaluate(
            "document.querySelector('#demo > .mvpl-grid > .mvpl-page').inert"
        )
        assert locked(page)

        page.keyboard.press("Escape")
        settle(page)
        assert box(page, "demo", "left")["right"] <= 1
        assert (
            page.evaluate("document.activeElement.getAttribute('aria-label')")
            == "Navigation"
        )
        assert not locked(page)

    def test_the_backdrop_closes_a_drawer(self, visit) -> None:
        page = visit("home", PHONE)
        page.locator(
            '#demo > .mvpl-grid > .mvpl-header [data-mvpl-toggle="right"]'
        ).click()
        settle(page)
        assert state(page, "demo")["right"]["visible"]
        page.mouse.click(20, 400)
        settle(page)
        assert not state(page, "demo")["right"]["visible"]

    def test_following_a_link_in_a_drawer_leaves_it_closed(self, visit) -> None:
        page = visit("home", PHONE)
        page.locator(
            '#demo > .mvpl-grid > .mvpl-header [data-mvpl-toggle="left"]'
        ).click()
        settle(page)
        page.locator(
            '#demo .mvpl-sidebar[data-side="left"] a[href$="/nested/"]'
        ).click()
        page.wait_for_load_state()
        assert not state(page, "demo")["left"]["visible"]


class TestThePlayground:
    def test_its_preview_toggles_leave_the_shell_alone(self, visit) -> None:
        page = visit("playground")
        page.locator(
            '#lp-layout .mvpl-sidebar[data-side="left"] [data-mvpl-toggle]'
        ).click()
        settle(page)
        assert box(page, "lp-layout", "left")["rail"]
        shell = state(page, "demo")
        assert shell["left"]["visible"]

    def test_a_drawer_in_the_preview_opens_inside_it_and_locks_nothing(
        self, visit
    ) -> None:
        page = visit("playground", PHONE)
        assert state(page, "lp-layout")["left"]["mode"] == "overlay"
        page.locator('#lp-layout header [data-mvpl-toggle="left"]').click()
        settle(page)
        frame = page.evaluate(
            "document.getElementById('lp-layout').getBoundingClientRect().left"
        )
        assert abs(box(page, "lp-layout", "left")["left"] - frame) < 2
        assert not locked(page)

    def test_a_typed_code_redraws_the_preview(self, visit) -> None:
        page = visit("playground")
        page.fill("#lp-code", "xyz")
        page.wait_for_function(
            "document.getElementById('lp-code').getAttribute('aria-invalid') === 'true'"
        )
        page.fill("#lp-code", "hHh LpR fFf")
        page.wait_for_function(
            "document.getElementById('lp-layout').dataset.mvplView === 'hHh LpR fFf'"
        )
        assert "view=hHh" in page.url
        # The swapped-in preview is mounted: its toggles are wired to their sidebars.
        controls = page.locator("#lp-layout [data-mvpl-toggle]").first.get_attribute(
            "aria-controls"
        )
        assert controls


class TestNestedLayouts:
    def test_an_inner_toggle_changes_only_the_inner_layout(self, visit) -> None:
        page = visit("nested")
        assert (
            page.evaluate(
                "document.getElementById('nl-document').parentElement.closest('[data-mvpl]').id"
            )
            == "nl-project"
        )
        outer, inner = state(page, "nl-project"), state(page, "nl-document")
        page.locator('#nl-document header [data-mvpl-toggle="right"]').click()
        settle(page)
        assert (
            state(page, "nl-document")["right"]["visible"] != inner["right"]["visible"]
        )
        assert state(page, "nl-project") == outer

    def test_a_layout_in_a_card_follows_the_card_width(self, visit) -> None:
        # The inbox card is narrow on a phone, so its folders are a drawer
        # there and docked on a desktop: container queries, not media queries.
        assert state(visit("nested", PHONE), "nl-inbox")["left"]["mode"] == "overlay"
        assert state(visit("nested"), "nl-inbox")["left"]["mode"] == "docked"

    def test_the_fixed_footer_stays_while_a_contained_layout_scrolls(
        self, visit
    ) -> None:
        page = visit("nested")
        page.evaluate(
            "document.querySelector('#nl-inbox > .mvpl-grid').scrollTop = 300"
        )
        settle(page, 150)
        gap = page.evaluate(
            "document.getElementById('nl-inbox').getBoundingClientRect().bottom"
            " - document.querySelector('#nl-inbox > .mvpl-grid > .mvpl-footer').getBoundingClientRect().bottom"
        )
        assert abs(gap) < 3

    def test_escape_closes_a_drawer_in_a_dialog_before_the_dialog(self, visit) -> None:
        page = visit("nested", PHONE)
        page.click("#nl-settings-open")
        settle(page)
        page.locator('#nl-settings-layout header [data-mvpl-toggle="left"]').click()
        settle(page)
        assert state(page, "nl-settings-layout")["left"]["visible"]
        page.keyboard.press("Escape")
        settle(page)
        assert not state(page, "nl-settings-layout")["left"]["visible"]
        assert page.evaluate("document.getElementById('nl-settings').open")
        page.keyboard.press("Escape")
        settle(page)
        assert not page.evaluate("document.getElementById('nl-settings').open")

    def test_a_sidebar_that_cannot_close_has_no_toggle(self, visit) -> None:
        page = visit("nested")
        page.click("#nl-settings-open")
        settle(page)
        assert state(page, "nl-settings-layout")["left"]["mode"] == "docked"
        visible = page.locator(
            '#nl-settings-layout [data-mvpl-toggle="left"]'
        ).evaluate_all("els => els.filter(el => el.checkVisibility())")
        assert visible == []


class TestWithoutCotton:
    def test_the_plain_template_layout_behaves_the_same(self, visit) -> None:
        page = visit("plain", PHONE)
        s = state(page, "app")
        assert s["left"]["mode"] == "overlay" and not s["left"]["visible"]
        page.locator('#app header [data-mvpl-toggle="left"]').first.click()
        settle(page)
        assert box(page, "app", "left")["role"] == "dialog"

    def test_its_sidebars_sit_beside_the_page_at_desktop_width(self, visit) -> None:
        s = state(visit("plain"), "app")
        assert s["left"]["mode"] == "docked" and s["left"]["visible"]


class TestScrollingPassesToThePage:
    # A sidebar or contained layout with nothing left to scroll hands the wheel
    # on to the page, as the browser does by default. Only a drawer keeps it.

    def test_the_wheel_over_a_fixed_sidebar_scrolls_the_page(self, visit) -> None:
        page = visit("nested")
        panel = page.locator(
            "#demo > .mvpl-grid > .mvpl-sidebar[data-side=left] > .mvpl-panel"
        )
        bounds = panel.bounding_box()
        page.mouse.move(bounds["x"] + 20, bounds["y"] + bounds["height"] - 40)
        page.mouse.wheel(0, 600)
        page.wait_for_function("window.scrollY > 0")

    def test_the_wheel_over_a_contained_layout_at_its_end_scrolls_the_page(
        self, visit
    ) -> None:
        page = visit("nested")
        page.evaluate(
            "const g = document.querySelector('#nl-inbox > .mvpl-grid'); g.scrollTop = g.scrollHeight;"
            "document.getElementById('nl-inbox').scrollIntoView({block: 'center'})"
        )
        before = page.evaluate("window.scrollY")
        # The middle of the card, which the scrolled page area is under.
        bounds = page.locator("#nl-inbox").bounding_box()
        page.mouse.move(
            bounds["x"] + bounds["width"] / 2, bounds["y"] + bounds["height"] / 2
        )
        page.mouse.wheel(0, 600)
        page.wait_for_function(f"window.scrollY > {before}")


class TestTheScriptApi:
    def test_a_layout_is_mounted_and_read_by_its_id(self, visit) -> None:
        page = visit("plain")
        assert page.evaluate("MvpLayout('app') === document.getElementById('app')")
        assert page.evaluate("MvpLayout.state('app').left.mode") == "docked"

    def test_a_sidebar_is_closed_and_opened_by_the_layout_id(self, visit) -> None:
        page = visit("plain")
        page.evaluate("MvpLayout.close('app', 'left')")
        settle(page)
        assert not state(page, "app")["left"]["visible"]
        page.evaluate("MvpLayout.open('app', 'left')")
        settle(page)
        assert state(page, "app")["left"]["visible"]
