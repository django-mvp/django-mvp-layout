"""Tests for the toggle component."""

import pytest

from tests.conftest import elements_of


def button_of(html):
    """Return the toggle's button as ``(name, attributes)``."""
    return next(found for found in elements_of(html) if found[0] == "button")


class TestToggle:
    """``<c-layout.toggle>``."""

    def test_with_no_side_it_controls_the_left_sidebar(self, render):
        assert button_of(render("<c-layout.toggle />"))[1]["data-mvpl-toggle"] == "left"

    @pytest.mark.parametrize("side", ["left", "right"])
    def test_it_controls_the_side_it_names(self, render, side):
        markup = render(f'<c-layout.toggle side="{side}" />')

        assert button_of(markup)[1]["data-mvpl-toggle"] == side

    def test_it_is_a_button_that_reports_it_is_not_expanded(self, render):
        attrs = button_of(render("<c-layout.toggle />"))[1]

        assert attrs["type"] == "button"
        assert attrs["aria-expanded"] == "false"
        assert "mvpl-toggle" in attrs["class"].split()

    @pytest.mark.parametrize("when", ["open", "closed"])
    def test_when_is_passed_to_the_markup_the_script_reads(self, render, when):
        markup = render(f'<c-layout.toggle when="{when}" />')

        assert button_of(markup)[1]["data-mvpl-when"] == when

    def test_without_when_it_is_always_shown(self, render):
        assert "data-mvpl-when" not in button_of(render("<c-layout.toggle />"))[1]

    def test_a_label_is_its_accessible_name(self, render):
        markup = render('<c-layout.toggle label="Folders" />')

        assert button_of(markup)[1]["aria-label"] == "Folders"

    def test_without_a_label_the_name_says_which_sidebar_it_controls(self, render):
        names = {
            side: button_of(render(f'<c-layout.toggle side="{side}" />'))[1][
                "aria-label"
            ]
            for side in ("left", "right")
        }

        assert all(names.values())
        assert names["left"] != names["right"]

    def test_class_and_other_attributes_are_added(self, render):
        attrs = button_of(render('<c-layout.toggle class="btn" data-x="1" />'))[1]

        assert attrs["class"].split() == ["mvpl-toggle", "btn"]
        assert attrs["data-x"] == "1"

    def test_its_content_is_the_icon(self, render):
        markup = render("<c-layout.toggle><i>menu</i></c-layout.toggle>")

        assert "<i>menu</i>" in markup
        assert "<svg" not in markup

    def test_with_no_content_it_draws_a_default_icon(self, render):
        markup = render("<c-layout.toggle />")

        assert "<svg" in markup

    def test_the_default_icon_is_hidden_from_assistive_technology(self, render):
        svg = next(
            attrs
            for tag, attrs in elements_of(render("<c-layout.toggle />"))
            if tag == "svg"
        )

        assert svg["aria-hidden"] == "true"
