"""Tests for a layout inside a box, and one inside another layout."""

import pytest

pytestmark = pytest.mark.django_db

OUTER = '#nl-project > .mvpl-grid > [data-mvpl-side="left"]'
INNER = '#nl-document > .mvpl-grid > [data-mvpl-side="left"]'
INNER_TOGGLE = '#nl-document > .mvpl-grid > .mvpl-header [data-mvpl-toggle="left"]'


def state_of(page, selector):
    """Read the attribute a sidebar's open or closed state is kept in."""
    return page.locator(selector).get_attribute("data-mvpl-state")


class TestNestedLayouts:
    """``<c-layout container>`` inside a card or inside another layout."""

    def test_a_contained_layout_carries_the_contained_attribute(self, render):
        markup = render("<c-layout container />")

        assert "data-mvpl-container" in markup

    def test_a_toggle_in_the_inner_layout_changes_only_the_inner_sidebar(
        self, visit, errors
    ):
        page = visit("components-nested")
        assert state_of(page, OUTER) == "open"
        assert state_of(page, INNER) == "open"

        page.locator(INNER_TOGGLE).click()

        assert state_of(page, INNER) == "closed"
        assert state_of(page, OUTER) == "open"
        assert errors == []

    def test_every_nested_layout_mounts_its_own_sidebars(self, visit):
        page = visit("components-nested")

        for selector in (OUTER, INNER):
            assert page.locator(selector).get_attribute("data-mvpl-behavior")
