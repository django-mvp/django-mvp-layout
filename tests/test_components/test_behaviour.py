"""Tests that a page written with components behaves in a browser."""

import pytest

pytestmark = pytest.mark.django_db

PHONE = {"width": 390, "height": 800}
LEFT = '#demo > .mvpl-grid > [data-mvpl-side="left"]'
RIGHT = '#demo > .mvpl-grid > [data-mvpl-side="right"]'


def state_of(page, selector):
    """Read the attribute a sidebar's open or closed state is kept in."""
    return page.locator(selector).get_attribute("data-mvpl-state")


class TestPageOfComponents:
    """The overview page, laid out with the six components."""

    def test_the_page_loads_with_no_script_error(self, visit, errors):
        visit("components-overview")

        assert errors == []

    def test_each_layout_is_mounted_before_the_page_finishes_loading(self, visit):
        page = visit("components-overview")

        assert page.locator("#demo[data-mvpl]").count() == 1
        assert page.evaluate("typeof MvpLayout") == "function"

    def test_a_toggle_closes_and_opens_the_sidebar_it_controls(self, visit):
        page = visit("components-overview")
        assert state_of(page, LEFT) == "open"

        page.locator(
            '#demo > .mvpl-grid > [data-mvpl-side="left"] [data-mvpl-toggle]'
        ).click()
        assert state_of(page, LEFT) == "closed"

        page.locator('.mvpl-header [data-mvpl-toggle="left"]').click()
        assert state_of(page, LEFT) == "open"

    def test_the_toggle_reports_whether_its_sidebar_is_open(self, visit):
        page = visit("components-overview")
        toggle = page.locator('.mvpl-header [data-mvpl-toggle="right"]')

        before = toggle.get_attribute("aria-expanded")
        toggle.click()

        assert toggle.get_attribute("aria-expanded") != before

    def test_a_sidebar_is_a_drawer_on_a_phone(self, visit):
        page = visit("components-overview", PHONE)

        assert page.locator(LEFT).get_attribute("data-mvpl-mode") == "overlay"


class TestPageWithoutTheScript:
    """A page that renders the components and loads no script."""

    def test_it_raises_no_error(self, visit, errors):
        visit("components-no-script")

        assert errors == []

    def test_it_is_drawn_in_its_server_rendered_state(self, visit):
        page = visit("components-no-script")

        assert page.locator("#app[data-mvpl]").count() == 1
        assert (
            page.locator('[data-mvpl-side="left"]').get_attribute("data-mvpl-state")
            == "open"
        )
