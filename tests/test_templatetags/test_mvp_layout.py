"""Tests for the template tags that write a layout's attributes."""

import pytest
from django.template import Context, Template
from django.test import RequestFactory

from mvp_layout.templatetags.mvp_layout import LayoutOptionError, layout_uid
from mvp_layout.view import LayoutViewError
from tests.conftest import attrs_of

DEFAULT_CODE = "hHh lpr fFf"


def render_tag(tag, context=None):
    """Render a tag inside a div and return that div's attributes."""
    source = "{% load mvp_layout %}<div " + tag + "></div>"
    return attrs_of(Template(source).render(Context(context or {})))


def style_variables(attrs):
    """Return a style attribute's custom properties, by name."""
    declarations = (part.split(":", 1) for part in attrs["style"].split(";") if part)
    return {name.strip(): value.strip() for name, value in declarations}


class TestLayoutAttrs:
    """The attributes written on a layout's root element."""

    def test_the_class_includes_the_layout_class_and_the_callers(self):
        attrs = render_tag('{% layout_attrs css_class="page-shell" %}')

        assert attrs["class"].split() == ["mvpl", "page-shell"]

    def test_the_class_is_the_layout_class_alone_without_a_caller_class(self):
        assert render_tag("{% layout_attrs %}")["class"] == "mvpl"

    def test_the_marker_attribute_is_present_and_bare(self):
        assert render_tag("{% layout_attrs %}")["data-mvpl"] is None

    def test_the_view_attribute_carries_the_normalised_code(self):
        attrs = render_tag('{% layout_attrs "lHh   LpR  lff" %}')

        assert attrs["data-mvpl-view"] == "lHh LpR lff"

    def test_no_view_means_the_default_code(self):
        assert render_tag("{% layout_attrs %}")["data-mvpl-view"] == DEFAULT_CODE

    def test_a_view_may_be_named(self):
        attrs = render_tag('{% layout_attrs view="lhh lpr lff" %}')

        assert attrs["data-mvpl-view"] == "lhh lpr lff"

    def test_a_view_may_come_from_the_context(self):
        attrs = render_tag("{% layout_attrs view %}", {"view": "lhr lpr lfr"})

        assert attrs["data-mvpl-view"] == "lhr lpr lfr"

    def test_the_container_attribute_is_present_only_with_container(self):
        contained = render_tag("{% layout_attrs container=True %}")
        plain = render_tag("{% layout_attrs %}")
        refused = render_tag("{% layout_attrs container=False %}")

        assert "data-mvpl-container" in contained
        assert "data-mvpl-container" not in plain
        assert "data-mvpl-container" not in refused

    @pytest.mark.parametrize(
        ("code", "fixed"),
        [
            ("hhh lpr fff", set()),
            ("hHh lpr fff", {"header"}),
            ("hhh lpr fFf", {"footer"}),
            ("hhh Lpr fff", {"left"}),
            ("hhh lpR fff", {"right"}),
            ("Hhh lpr fff", {"header"}),
            ("hhH lpr fff", {"header"}),
            ("hhh lpr ffF", {"footer"}),
            ("hhh lpr Fff", {"footer"}),
            ("lHh LpR lFf", {"header", "left", "right", "footer"}),
        ],
    )
    def test_each_fixed_attribute_is_present_exactly_when_its_area_is_fixed(
        self, code, fixed
    ):
        attrs = render_tag("{% layout_attrs view %}", {"view": code})

        written = {
            area
            for area in ("header", "left", "right", "footer")
            if f"data-mvpl-{area}-fixed" in attrs
        }
        assert written == fixed

    def test_the_style_carries_the_areas_and_the_four_offsets(self):
        variables = style_variables(render_tag('{% layout_attrs "lHh lpr lFf" %}'))

        assert variables == {
            "--mvpl-areas": (
                "'left header header' 'left page right' 'left footer footer'"
            ),
            "--mvpl-left-top": "0px",
            "--mvpl-left-bottom": "0px",
            "--mvpl-right-top": "var(--mvpl-header-h, 0px)",
            "--mvpl-right-bottom": "var(--mvpl-footer-h, 0px)",
        }

    def test_the_style_appends_the_callers_style(self):
        attrs = render_tag('{% layout_attrs style="height: 20rem" %}')

        assert style_variables(attrs)["height"] == "20rem"
        assert "--mvpl-areas" in style_variables(attrs)

    def test_the_style_is_only_the_layouts_without_a_caller_style(self):
        names = set(style_variables(render_tag("{% layout_attrs %}")))

        assert names == {
            "--mvpl-areas",
            "--mvpl-left-top",
            "--mvpl-left-bottom",
            "--mvpl-right-top",
            "--mvpl-right-bottom",
        }

    def test_every_argument_may_be_named(self):
        attrs = render_tag(
            '{% layout_attrs view="lhh lpr lff" container=True '
            'css_class="x" style="y: 1" %}'
        )

        assert attrs["data-mvpl-view"] == "lhh lpr lff"
        assert "data-mvpl-container" in attrs
        assert attrs["class"] == "mvpl x"
        assert style_variables(attrs)["y"] == "1"

    def test_the_caller_class_is_escaped(self):
        html = Template(
            "{% load mvp_layout %}<div {% layout_attrs css_class=hostile %}></div>"
        ).render(Context({"hostile": '"><script>'}))

        assert "<script>" not in html
        assert attrs_of(html)["class"] == 'mvpl "><script>'

    def test_a_wrong_code_raises_when_the_template_renders(self):
        template = Template('{% load mvp_layout %}<div {% layout_attrs "lpr" %}>')

        with pytest.raises(LayoutViewError) as refusal:
            template.render(Context())

        assert "'lpr'" in str(refusal.value)


def request_with(**cookies):
    """Return a request carrying the cookies, named by their mvpl- suffix."""
    factory = RequestFactory()
    for name, value in cookies.items():
        factory.cookies["mvpl-" + name] = value
    return factory.get("/")


class TestSidebarAttrs:
    """The attributes written on a sidebar's aside."""

    def test_the_defaults_for_a_left_sidebar(self):
        attrs = render_tag("{% sidebar_attrs %}")

        assert attrs["class"] == "mvpl-sidebar"
        assert attrs["data-mvpl-side"] == "left"
        assert attrs["data-mvpl-collapse"] == "offcanvas"
        assert attrs["data-mvpl-behavior"] == "auto"
        assert attrs["data-mvpl-breakpoint"] == "lg"
        assert attrs["data-mvpl-state"] == "open"

    def test_a_right_sidebar_defaults_to_the_xl_breakpoint(self):
        attrs = render_tag('{% sidebar_attrs "right" %}')

        assert attrs["data-mvpl-side"] == "right"
        assert attrs["data-mvpl-breakpoint"] == "xl"

    def test_the_side_may_be_named(self):
        assert render_tag('{% sidebar_attrs side="right" %}')["data-mvpl-side"] == (
            "right"
        )

    def test_the_class_includes_the_callers(self):
        attrs = render_tag('{% sidebar_attrs css_class="wide nav" %}')

        assert attrs["class"].split() == ["mvpl-sidebar", "wide", "nav"]

    @pytest.mark.parametrize(
        ("option", "choice"),
        [
            ("side", "left"),
            ("side", "right"),
            ("collapse", "offcanvas"),
            ("collapse", "icons"),
            ("collapse", "none"),
            ("behavior", "auto"),
            ("behavior", "docked"),
            ("behavior", "overlay"),
            ("breakpoint", "sm"),
            ("breakpoint", "md"),
            ("breakpoint", "lg"),
            ("breakpoint", "xl"),
            ("breakpoint", "2xl"),
        ],
    )
    def test_every_choice_is_written(self, option, choice):
        attrs = render_tag(f'{{% sidebar_attrs {option}="{choice}" %}}')

        assert attrs[f"data-mvpl-{option}"] == choice

    @pytest.mark.parametrize(
        ("option", "choices"),
        [
            ("side", ["left", "right"]),
            ("collapse", ["offcanvas", "icons", "none"]),
            ("behavior", ["auto", "docked", "overlay"]),
            ("breakpoint", ["sm", "md", "lg", "xl", "2xl"]),
        ],
    )
    def test_an_option_outside_its_choices_names_the_choices(self, option, choices):
        template = Template(
            "{% load mvp_layout %}<aside {% sidebar_attrs " + option + '="huge" %}>'
        )

        with pytest.raises(LayoutOptionError) as refusal:
            template.render(Context())

        assert all(choice in str(refusal.value) for choice in choices)
        assert "huge" in str(refusal.value)

    def test_the_option_error_is_a_value_error(self):
        assert issubclass(LayoutOptionError, ValueError)

    def test_width_and_rail_width_are_written_as_variables(self):
        attrs = render_tag('{% sidebar_attrs width="20rem" rail_width="4rem" %}')

        assert style_variables(attrs) == {"--mvpl-w": "20rem", "--mvpl-rail-w": "4rem"}

    def test_a_drawer_width_is_written_as_a_variable(self):
        attrs = render_tag('{% sidebar_attrs drawer_width="22rem" %}')

        assert style_variables(attrs) == {"--mvpl-drawer-w": "22rem"}

    def test_a_transition_is_written_as_a_variable(self):
        attrs = render_tag('{% sidebar_attrs transition="300ms" %}')

        assert style_variables(attrs) == {"--mvpl-transition": "300ms"}

    def test_no_style_is_written_without_a_width(self):
        assert "style" not in render_tag("{% sidebar_attrs %}")

    def test_only_the_width_given_is_written(self):
        attrs = render_tag('{% sidebar_attrs rail_width="3rem" %}')

        assert style_variables(attrs) == {"--mvpl-rail-w": "3rem"}

    def test_an_empty_persist_name_means_none_given(self):
        attrs = render_tag('{% sidebar_attrs persist="" %}')

        assert "data-mvpl-persist" not in attrs

    def test_the_persist_name_is_written_only_when_given(self):
        named = render_tag('{% sidebar_attrs persist="nav" %}')
        anonymous = render_tag("{% sidebar_attrs %}")

        assert named["data-mvpl-persist"] == "nav"
        assert "data-mvpl-persist" not in anonymous

    def test_closed_draws_the_sidebar_closed(self):
        assert render_tag("{% sidebar_attrs closed=True %}")["data-mvpl-state"] == (
            "closed"
        )

    def test_closed_false_draws_the_sidebar_open(self):
        assert render_tag("{% sidebar_attrs closed=False %}")["data-mvpl-state"] == (
            "open"
        )

    @pytest.mark.parametrize(
        ("tag", "rail"),
        [
            ('{% sidebar_attrs collapse="icons" closed=True %}', True),
            ('{% sidebar_attrs collapse="icons" %}', False),
            ('{% sidebar_attrs collapse="offcanvas" closed=True %}', False),
            ('{% sidebar_attrs collapse="none" closed=True %}', False),
            (
                '{% sidebar_attrs collapse="icons" behavior="overlay" closed=True %}',
                False,
            ),
            (
                '{% sidebar_attrs collapse="icons" behavior="docked" closed=True %}',
                True,
            ),
        ],
    )
    def test_the_rail_attribute_marks_a_closed_icon_sidebar_that_is_not_overlay(
        self, tag, rail
    ):
        attrs = render_tag(tag)

        assert ("data-mvpl-rail" in attrs) is rail
        if rail:
            assert attrs["data-mvpl-rail"] is None


class TestSidebarPersistName:
    @pytest.mark.parametrize(
        ("name", "allowed"),
        [
            ("nav", True),
            ("left-nav", True),
            ("nav_2", True),
            ("NAV9", True),
            ("my nav", False),
            ("a;b", False),
            ("a=b", False),
            ("a/b", False),
        ],
    )
    def test_a_name_is_kept_only_when_it_is_safe_in_a_cookie_name(self, name, allowed):
        tag = "{% sidebar_attrs persist=name %}"
        if allowed:
            assert render_tag(tag, {"name": name})["data-mvpl-persist"] == name
            return
        with pytest.raises(LayoutOptionError) as refusal:
            render_tag(tag, {"name": name})
        assert "A-Za-z0-9_-" in str(refusal.value)


class TestSidebarCookie:
    """The state a sidebar is drawn in, from the cookie its persist name reads."""

    @pytest.mark.parametrize("remembered", ["open", "closed"])
    def test_the_cookie_overrides_the_state(self, remembered):
        other = "open" if remembered == "closed" else "closed"
        closed = remembered == "open"
        request = request_with(nav=remembered)

        attrs = render_tag(
            '{% sidebar_attrs persist="nav" closed=closed %}',
            {"request": request, "closed": closed},
        )

        assert attrs["data-mvpl-state"] == remembered
        assert attrs["data-mvpl-state"] != other

    def test_a_remembered_closed_icon_sidebar_is_drawn_as_a_rail(self):
        attrs = render_tag(
            '{% sidebar_attrs collapse="icons" persist="nav" %}',
            {"request": request_with(nav="closed")},
        )

        assert attrs["data-mvpl-state"] == "closed"
        assert "data-mvpl-rail" in attrs

    @pytest.mark.parametrize("value", ["shut", "OPEN", "", "1"])
    def test_any_other_cookie_value_is_ignored(self, value):
        attrs = render_tag(
            '{% sidebar_attrs persist="nav" closed=True %}',
            {"request": request_with(nav=value)},
        )

        assert attrs["data-mvpl-state"] == "closed"

    def test_no_request_in_the_context_renders_the_options_state(self):
        attrs = render_tag('{% sidebar_attrs persist="nav" closed=True %}')

        assert attrs["data-mvpl-state"] == "closed"

    def test_no_persist_name_remembers_nothing(self):
        attrs = render_tag(
            "{% sidebar_attrs %}", {"request": request_with(nav="closed")}
        )

        assert attrs["data-mvpl-state"] == "open"

    def test_a_cookie_for_another_name_is_not_read(self):
        attrs = render_tag(
            '{% sidebar_attrs persist="nav" %}',
            {"request": request_with(tools="closed")},
        )

        assert attrs["data-mvpl-state"] == "open"

    @pytest.mark.parametrize("remembered", ["open", "closed"])
    def test_collapse_none_is_always_open(self, remembered):
        attrs = render_tag(
            '{% sidebar_attrs collapse="none" persist="nav" closed=True %}',
            {"request": request_with(nav=remembered)},
        )

        assert attrs["data-mvpl-state"] == "open"

    def test_two_sidebars_with_one_persist_name_read_the_same_cookie(self):
        context = {"request": request_with(nav="closed")}

        left = render_tag('{% sidebar_attrs "left" persist="nav" %}', context)
        right = render_tag('{% sidebar_attrs "right" persist="nav" %}', context)

        assert left["data-mvpl-state"] == right["data-mvpl-state"] == "closed"


class TestLayoutUid:
    """The id given to a layout or sidebar that was not given one."""

    def test_it_starts_with_the_prefix_and_has_a_twelve_character_suffix(self):
        prefix, _, suffix = layout_uid("sidebar").partition("-")

        assert prefix == "sidebar"
        assert len(suffix) == 12

    def test_a_thousand_ids_are_all_different(self):
        assert len({layout_uid("layout") for _ in range(1000)}) == 1000

    def test_it_is_a_tag_that_can_name_a_variable(self):
        html = Template(
            '{% load mvp_layout %}{% layout_uid "layout" as id %}<i id="{{ id }}"></i>'
        ).render(Context())

        assert attrs_of(html)["id"].startswith("layout-")
