"""Template tags that write a layout's attributes.

The ``<c-layout>`` components are built on these, and a template that doesn't
use django-cotton calls them itself::

    {% load mvp_layout %}
    <div {% layout_attrs "lHh LpR lff" %}>
      <div class="mvpl-grid">
        <header class="mvpl-header">…</header>
        <aside {% sidebar_attrs "left" persist="nav" %} aria-label="Navigation">…</aside>
        <main class="mvpl-page">…</main>
      </div>
    </div>
"""

from django import template
from django.utils.html import format_html, format_html_join
from django.utils.safestring import SafeString

from mvp_layout.view import LayoutView

register = template.Library()


def write_attrs(pairs: list[tuple[str, object]]) -> SafeString:
    """Write attributes as HTML.

    Args:
        pairs: Attribute names and values. ``True`` writes a bare attribute, and
            ``False``, ``None`` and an empty string leave it out.

    Returns:
        The attributes, escaped, separated by spaces.
    """
    present = [(name, value) for name, value in pairs if value not in (None, False, "")]
    return format_html_join(
        " ",
        "{}",
        (
            (name if value is True else format_html('{}="{}"', name, value),)
            for name, value in present
        ),
    )


@register.simple_tag
def layout_attrs(view=None, container=False, css_class="", style=""):
    """Write the attributes of a layout's root element, from its layout code.

    Args:
        view: The layout code. Without one the layout uses the default code.
        container: Make the layout fill the box it is placed in and scroll
            inside it.
        css_class: Classes added to the layout's own.
        style: Declarations added after the layout's own.

    Returns:
        The attributes, ready to place inside a tag.

    Raises:
        LayoutViewError: The view is not a layout code.
    """
    layout = LayoutView.parse(view)
    variables = (
        f"--mvpl-areas: {layout.areas}; "
        f"--mvpl-left-top: {layout.left_top}; "
        f"--mvpl-left-bottom: {layout.left_bottom}; "
        f"--mvpl-right-top: {layout.right_top}; "
        f"--mvpl-right-bottom: {layout.right_bottom};"
    )
    return write_attrs(
        [
            ("class", f"mvpl {css_class}".strip()),
            ("data-mvpl", True),
            ("data-mvpl-view", layout.code),
            ("data-mvpl-container", bool(container)),
            ("data-mvpl-header-fixed", layout.header_fixed),
            ("data-mvpl-left-fixed", layout.left_fixed),
            ("data-mvpl-right-fixed", layout.right_fixed),
            ("data-mvpl-footer-fixed", layout.footer_fixed),
            ("style", f"{variables} {style}".strip()),
        ]
    )
