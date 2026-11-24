"""The tags that write a layout's and a sidebar's attributes."""

import pytest
from django.template import Context, Template
from django.test import RequestFactory

from mvp_layout.templatetags.mvp_layout import LayoutOptionError
from mvp_layout.view import LayoutViewError


def render(source, request=None, **context):
    if request is not None:
        context["request"] = request
    return Template("{% load mvp_layout %}" + source).render(Context(context))


def with_cookies(**cookies):
    request = RequestFactory().get("/")
    request.COOKIES.update(cookies)
    return request


class TestLayoutAttrs:
    def test_it_writes_the_areas_the_grid_reads(self) -> None:
        html = render('<div {% layout_attrs "lHh LpR lff" %}></div>')
        assert "--mvpl-areas: &#x27;left header header&#x27;" in html
        assert 'data-mvpl-view="lHh LpR lff"' in html

    def test_fixed_areas_are_flagged(self) -> None:
        html = render('<div {% layout_attrs "hHh lpr fff" %}></div>')
        assert "data-mvpl-header-fixed" in html
        assert "data-mvpl-footer-fixed" not in html

    def test_container_is_a_bare_attribute(self) -> None:
        assert "data-mvpl-container" in render(
            '<div {% layout_attrs "hHh lpr fFf" True %}></div>'
        )
        assert "data-mvpl-container" not in render(
            '<div {% layout_attrs "hHh lpr fFf" %}></div>'
        )

    def test_a_wrong_code_raises(self) -> None:
        with pytest.raises(LayoutViewError):
            render('<div {% layout_attrs "nope" %}></div>')

    def test_caller_class_and_style_are_kept(self) -> None:
        html = render(
            '<div {% layout_attrs css_class="h-96" style="color: red;" %}></div>'
        )
        assert 'class="mvpl h-96"' in html
        assert "color: red;" in html


class TestSidebarAttrs:
    def test_defaults_per_side(self) -> None:
        left = render('{% sidebar_attrs "left" %}')
        right = render('{% sidebar_attrs "right" %}')
        assert 'data-breakpoint="lg"' in left
        assert 'data-breakpoint="xl"' in right
        assert 'data-state="open"' in left

    def test_closed_starts_closed(self) -> None:
        assert 'data-state="closed"' in render('{% sidebar_attrs "left" closed=True %}')

    def test_a_remembered_state_wins(self) -> None:
        request = with_cookies(**{"mvpl-nav": "closed"})
        html = render('{% sidebar_attrs "left" persist="nav" %}', request)
        assert 'data-state="closed"' in html
        assert 'data-persist="nav"' in html

    def test_a_remembered_open_state_beats_closed(self) -> None:
        request = with_cookies(**{"mvpl-nav": "open"})
        html = render('{% sidebar_attrs "left" persist="nav" closed=True %}', request)
        assert 'data-state="open"' in html

    def test_a_cookie_with_another_value_is_ignored(self) -> None:
        request = with_cookies(**{"mvpl-nav": "<script>"})
        html = render('{% sidebar_attrs "left" persist="nav" %}', request)
        assert 'data-state="open"' in html

    def test_without_persist_no_cookie_is_read(self) -> None:
        request = with_cookies(**{"mvpl-nav": "closed"})
        assert 'data-state="open"' in render('{% sidebar_attrs "left" %}', request)

    def test_a_sidebar_that_never_closes_is_drawn_open(self) -> None:
        html = render('{% sidebar_attrs "left" collapse="none" closed=True %}')
        assert 'data-state="open"' in html

    def test_a_closed_icon_sidebar_is_drawn_as_a_rail(self) -> None:
        html = render('{% sidebar_attrs "left" collapse="icons" closed=True %}')
        assert "data-mvpl-rail" in html

    def test_an_overlay_sidebar_is_never_a_rail(self) -> None:
        html = render(
            '{% sidebar_attrs "left" collapse="icons" behavior="overlay" closed=True %}'
        )
        assert "data-mvpl-rail" not in html

    def test_widths_are_css_variables(self) -> None:
        html = render('{% sidebar_attrs "left" width="20rem" rail_width="5rem" %}')
        assert "--mvpl-w: 20rem;" in html
        assert "--mvpl-rail-w: 5rem;" in html

    @pytest.mark.parametrize(
        "option",
        [
            '"middle"',
            '"left" collapse="hidden"',
            '"left" breakpoint="xxl"',
            '"left" behavior="float"',
        ],
    )
    def test_an_option_that_is_not_a_choice_raises(self, option) -> None:
        with pytest.raises(LayoutOptionError):
            render("{% sidebar_attrs " + option + " %}")

    def test_values_are_escaped(self) -> None:
        html = render('{% sidebar_attrs "left" persist=name %}', name='"><b>')
        assert "<b>" not in html


class TestLayoutUid:
    def test_ids_differ(self) -> None:
        assert render('{% layout_uid "x" %}') != render('{% layout_uid "x" %}')
