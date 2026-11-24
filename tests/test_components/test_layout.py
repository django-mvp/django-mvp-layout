"""Tests for the layout component and its three plain areas."""

import pytest
from django.template import Context, Template

from mvp_layout.view import LayoutViewError
from tests.conftest import attrs_of, elements_of, with_data


def plain_layout(args):
    """Render the layout tag's attributes on a div, as a plain template does."""
    source = "{% load mvp_layout %}<div " + args + "></div>"
    return Template(source).render(Context())


def layout_of(html):
    """Return the attributes of the first element, the layout's root."""
    return attrs_of(html)


class TestLayout:
    """``<c-layout>``, the root of a layout."""

    def test_it_carries_the_attributes_the_tag_writes_for_its_code(self, render):
        markup = render('<c-layout view="lHh LpR lff" id="app" />')

        assert with_data(markup)[0] == with_data(
            plain_layout('{% layout_attrs "lHh LpR lff" %}')
        )[0]

    def test_a_layout_with_no_code_is_the_tags_default(self, render):
        assert with_data(render("<c-layout />"))[0] == with_data(
            plain_layout("{% layout_attrs %}")
        )[0]

    def test_a_wrong_code_fails_with_the_tags_error(self, render):
        with pytest.raises(LayoutViewError):
            render('<c-layout view="nonsense" />')

    def test_a_contained_layout_carries_the_contained_attribute(self, render):
        markup = render("<c-layout container />")

        assert with_data(markup)[0] == with_data(
            plain_layout("{% layout_attrs container=True %}")
        )[0]

    def test_a_layout_without_container_is_not_contained(self, render):
        assert "data-mvpl-container" not in layout_of(render("<c-layout />"))

    def test_a_given_id_is_used_as_written(self, render):
        assert layout_of(render('<c-layout id="app" />'))["id"] == "app"

    def test_two_layouts_without_ids_get_different_ids(self, render):
        markup = render("<c-layout /><c-layout />")
        ids = [attrs["id"] for _, attrs in elements_of(markup) if "data-mvpl" in attrs]

        assert len(ids) == 2
        assert len(set(ids)) == 2

    def test_class_and_style_are_added_to_the_layouts_own(self, render):
        attrs = layout_of(render('<c-layout class="frame" style="height: 9rem" />'))

        assert attrs["class"].split() == ["mvpl", "frame"]
        assert attrs["style"].endswith("height: 9rem")
        assert attrs["style"].startswith("--mvpl-areas:")

    def test_any_other_attribute_is_added_to_the_layout(self, render):
        assert layout_of(render('<c-layout data-extra="1" />'))["data-extra"] == "1"

    def test_the_layout_mounts_itself_by_its_id_after_its_markup(self, render):
        markup = render('<c-layout id="app" />')

        assert markup.strip().endswith('MvpLayout("app");</script>')

    def test_the_mount_call_is_guarded_for_a_page_without_the_script(self, render):
        assert "window.MvpLayout && MvpLayout(" in render("<c-layout />")

    def test_the_mount_call_escapes_an_id_a_script_string_cannot_hold(self, render):
        markup = render("<c-layout :id=\"ident\" />", ident='a"b')

        assert 'MvpLayout("a\\u0022b")' in markup

    def test_the_areas_are_drawn_inside_the_grid_in_the_order_written(self, render):
        markup = render(
            "<c-layout><c-layout.header /><c-layout.page /><c-layout.footer />"
            "</c-layout>"
        )
        classes = [
            attrs["class"].split()[0]
            for _, attrs in elements_of(markup)
            if attrs.get("class", "").startswith("mvpl-")
        ]

        assert classes == ["mvpl-grid", "mvpl-header", "mvpl-page", "mvpl-footer"]


class TestAreas:
    """``<c-layout.header>``, ``<c-layout.page>`` and ``<c-layout.footer>``."""

    @pytest.mark.parametrize(
        ("name", "element"),
        [("header", "header"), ("footer", "footer")],
    )
    def test_an_area_is_its_element_with_its_class(self, render, name, element):
        tag, attrs = elements_of(render(f"<c-layout.{name} />"))[0]

        assert tag == element
        assert f"mvpl-{name}" in attrs["class"].split()

    @pytest.mark.parametrize("name", ["header", "page", "footer"])
    def test_an_area_carries_class_and_any_other_attribute(self, render, name):
        _, attrs = elements_of(render(f'<c-layout.{name} class="x" data-y="2" />'))[0]

        assert attrs["class"].split() == [f"mvpl-{name}", "x"]
        assert attrs["data-y"] == "2"

    @pytest.mark.parametrize("name", ["header", "page", "footer"])
    def test_an_area_draws_its_content(self, render, name):
        assert "<b>in</b>" in render(f"<c-layout.{name}><b>in</b></c-layout.{name}>")

    def test_the_page_is_a_main_when_asked(self, render):
        assert elements_of(render('<c-layout.page tag="main" />'))[0][0] == "main"

    @pytest.mark.parametrize("markup", ["<c-layout.page />", '<c-layout.page tag="p" />'])
    def test_the_page_is_otherwise_a_div(self, render, markup):
        assert elements_of(render(markup))[0][0] == "div"

    def test_the_page_keeps_its_class_whichever_element_it_is(self, render):
        for tag in ("main", "div"):
            attrs = elements_of(render(f'<c-layout.page tag="{tag}" class="z" />'))[0][1]

            assert "z" in attrs["class"].split()

