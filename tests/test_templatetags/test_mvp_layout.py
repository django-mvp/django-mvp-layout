"""Tests for the template tags that write a layout's attributes."""

from html.parser import HTMLParser

import pytest
from django.template import Context, Template

from mvp_layout.view import LayoutViewError

DEFAULT_CODE = "hHh lpr fFf"


class TagReader(HTMLParser):
    """Collects the attributes of the first start tag in a piece of HTML."""

    def __init__(self):
        super().__init__()
        self.attrs = None

    def handle_starttag(self, tag, attrs):
        if self.attrs is None:
            self.attrs = dict(attrs)


def attrs_of(html):
    """Return the attributes of the first tag in the HTML, by name."""
    reader = TagReader()
    reader.feed(html)
    return reader.attrs


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
            "--mvpl-areas": "'left header header' 'left page right' 'left footer footer'",
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
            '{% layout_attrs view="lhh lpr lff" container=True css_class="x" style="y: 1" %}'
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
