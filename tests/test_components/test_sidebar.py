"""Tests for the sidebar component."""

import pytest
from django.template import Context, Template
from django.test import RequestFactory

from mvp_layout.templatetags.mvp_layout import LayoutOptionError
from tests.conftest import elements_of, with_data

# Each row is a sidebar written both ways: the component's attributes and the
# tag's arguments for the same options.
OPTIONS = [
    pytest.param("", "", id="none"),
    pytest.param('side="right"', 'side="right"', id="right"),
    pytest.param('collapse="icons"', 'collapse="icons"', id="icons"),
    pytest.param('collapse="none"', 'collapse="none"', id="no collapse"),
    pytest.param('breakpoint="sm"', 'breakpoint="sm"', id="breakpoint"),
    pytest.param('behavior="overlay"', 'behavior="overlay"', id="overlay"),
    pytest.param('behavior="docked"', 'behavior="docked"', id="docked"),
    pytest.param('width="12rem"', 'width="12rem"', id="width"),
    pytest.param(
        'collapse="icons" rail-width="3rem" closed',
        'collapse="icons" rail_width="3rem" closed=True',
        id="rail width and closed",
    ),
    pytest.param('persist="nav"', 'persist="nav"', id="persist"),
    pytest.param('side="right" class="x"', 'side="right" css_class="x"', id="class"),
]


def plain_sidebar(tag_args, request=None):
    """Render the sidebar tag's attributes on an aside, as a plain template does."""
    source = "{% load mvp_layout %}<aside {% sidebar_attrs " + tag_args + " %}></aside>"
    return Template(source).render(Context({"request": request}))


def sidebar_of(html):
    """Return the aside the component drew."""
    return next(found for found in elements_of(html) if found[0] == "aside")


class TestSidebar:
    """``<c-layout.sidebar>``."""

    @pytest.mark.parametrize(("attributes", "tag_args"), OPTIONS)
    def test_it_carries_the_attributes_the_tag_writes_for_the_same_options(
        self, render, attributes, tag_args
    ):
        markup = render(f"<c-layout.sidebar {attributes}>x</c-layout.sidebar>")

        assert with_data(markup)[0] == with_data(plain_sidebar(tag_args))[0]

    @pytest.mark.parametrize(
        "attributes",
        ['side="up"', 'collapse="slide"', 'breakpoint="huge"', 'behavior="never"'],
    )
    def test_an_option_outside_its_choices_fails_with_the_tags_error(
        self, render, attributes
    ):
        with pytest.raises(LayoutOptionError) as refusal:
            render(f"<c-layout.sidebar {attributes}>x</c-layout.sidebar>")

        assert "Choose one of" in str(refusal.value)

    @pytest.mark.parametrize("remembered", ["open", "closed"])
    def test_it_is_drawn_in_the_state_a_remembered_cookie_gives(
        self, render, remembered
    ):
        factory = RequestFactory()
        factory.cookies["mvpl-nav"] = remembered
        get = factory.get("/")

        markup = render(
            '<c-layout.sidebar persist="nav">x</c-layout.sidebar>', request=get
        )

        assert sidebar_of(markup)[1]["data-mvpl-state"] == remembered
        assert (
            with_data(markup)[0]
            == with_data(plain_sidebar('persist="nav"', request=get))[0]
        )

    def test_its_label_is_its_accessible_name(self, render):
        markup = render('<c-layout.sidebar label="Navigation">x</c-layout.sidebar>')

        assert sidebar_of(markup)[1]["aria-label"] == "Navigation"

    def test_it_has_no_accessible_name_when_none_is_given(self, render):
        assert (
            "aria-label"
            not in sidebar_of(render("<c-layout.sidebar>x</c-layout.sidebar>"))[1]
        )

    def test_a_given_id_is_used_as_written(self, render):
        markup = render('<c-layout.sidebar id="nav">x</c-layout.sidebar>')

        assert sidebar_of(markup)[1]["id"] == "nav"

    def test_sidebars_without_ids_get_different_ids(self, render):
        markup = render(
            "<c-layout.sidebar>x</c-layout.sidebar>"
            '<c-layout.sidebar side="right">y</c-layout.sidebar>'
        )
        ids = [attrs["id"] for tag, attrs in elements_of(markup) if tag == "aside"]

        assert len(set(ids)) == 2

    def test_a_generated_id_names_the_kind_of_element(self, render):
        markup = render("<c-layout.sidebar>x</c-layout.sidebar>")

        assert sidebar_of(markup)[1]["id"].startswith("sidebar-")

    def test_any_other_attribute_is_added(self, render):
        markup = render('<c-layout.sidebar data-extra="1">x</c-layout.sidebar>')

        assert sidebar_of(markup)[1]["data-extra"] == "1"

    def test_its_content_sits_in_the_panel_behind_a_backdrop(self, render):
        markup = render("<c-layout.sidebar><b>in</b></c-layout.sidebar>")
        classes = [attrs.get("class") for _, attrs in elements_of(markup)]

        assert classes[1:3] == ["mvpl-backdrop", "mvpl-panel"]
        assert "<b>in</b>" in markup

    @pytest.mark.parametrize("content", ["", " ", "\n   \n"])
    def test_with_no_content_nothing_is_drawn(self, render, content):
        markup = render(f"<c-layout.sidebar>{content}</c-layout.sidebar>")

        assert "<aside" not in markup
        assert markup.strip() == ""
