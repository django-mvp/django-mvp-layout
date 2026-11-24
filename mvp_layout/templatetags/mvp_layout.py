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

import uuid
from dataclasses import dataclass

from django import template
from django.utils.html import format_html, format_html_join
from django.utils.safestring import SafeString

from mvp_layout.view import LayoutView

register = template.Library()

STATES = ("open", "closed")
COLLAPSES = ("offcanvas", "icons", "none")
BEHAVIORS = ("auto", "docked", "overlay")
BREAKPOINTS = ("sm", "md", "lg", "xl", "2xl")
DEFAULT_BREAKPOINTS = {"left": "lg", "right": "xl"}
COOKIE_PREFIX = "mvpl-"


class LayoutOptionError(ValueError):
    """A sidebar option that is not one of its choices."""


@dataclass(frozen=True)
class Sidebar:
    """A sidebar's options, settled, and the state the server draws it in."""

    side: str
    collapse: str
    behavior: str
    breakpoint: str
    state: str

    @property
    def rail(self) -> bool:
        """Closed to its icon rail beside the page, as drawn before any script runs."""
        return (
            self.state == "closed"
            and self.collapse == "icons"
            and self.behavior != "overlay"
        )


def choose(name: str, value: object, choices: tuple[str, ...], default: str) -> str:
    """Return the value when it is one of the choices, the default when none was given."""
    if value in (None, ""):
        return default
    if value not in choices:
        allowed = ", ".join(choices)
        raise LayoutOptionError(
            f"{value!r} is not a sidebar {name}. Choose one of: {allowed}."
        )
    return str(value)


def settle_sidebar(
    side: object,
    *,
    collapse: object = None,
    breakpoint: object = None,  # noqa: A002 - the option's name in the markup
    behavior: object = None,
    persist: object = None,
    closed: object = False,
    cookies: dict | None = None,
) -> Sidebar:
    """Settle a sidebar's options and read the state the reader left it in.

    The state comes from the cookie the layout script writes, so a sidebar the
    reader closed is drawn closed and never opens and snaps shut on load.
    """
    side = choose("side", side, ("left", "right"), "left")
    collapse = choose("collapse", collapse, COLLAPSES, "offcanvas")
    behavior = choose("behavior", behavior, BEHAVIORS, "auto")
    breakpoint = choose(  # noqa: A001
        "breakpoint", breakpoint, BREAKPOINTS, DEFAULT_BREAKPOINTS[side]
    )
    state = "closed" if closed else "open"
    if persist and cookies:
        remembered = cookies.get(COOKIE_PREFIX + str(persist))
        if remembered in STATES:
            state = remembered
    if collapse == "none":
        state = "open"
    return Sidebar(side, collapse, behavior, breakpoint, state)


def cookies_of(context) -> dict:
    """Return the request's cookies, or none when the context has no request."""
    request = context.get("request")
    return request.COOKIES if request is not None else {}


def write_attrs(pairs: list[tuple[str, object]]) -> SafeString:
    """Attributes as HTML. True writes a bare attribute, False and None leave it out."""
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
def layout_view(code):
    """Read a layout code. A wrong code raises, naming the rules."""
    return LayoutView.parse(code)


@register.simple_tag
def layout_uid(prefix="mvpl"):
    """Return an id for an element that was not given one."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


@register.simple_tag
def layout_attrs(view=None, container=False, css_class="", style=""):
    """Write the attributes of a layout's root element, from its layout code.

    ``container`` makes the layout fill the box it is placed in and scroll
    inside it. ``css_class`` and ``style`` are added to the layout's own.
    """
    lv = LayoutView.parse(view)
    variables = (
        f"--mvpl-areas: {lv.areas}; "
        f"--mvpl-left-top: {lv.left_top}; --mvpl-left-bottom: {lv.left_bottom}; "
        f"--mvpl-right-top: {lv.right_top}; --mvpl-right-bottom: {lv.right_bottom};"
    )
    return write_attrs(
        [
            ("class", f"mvpl {css_class}".strip()),
            ("data-mvpl", True),
            ("data-mvpl-view", lv.code),
            ("data-mvpl-container", bool(container)),
            ("data-mvpl-header-fixed", lv.header_fixed),
            ("data-mvpl-left-fixed", lv.left_fixed),
            ("data-mvpl-right-fixed", lv.right_fixed),
            ("data-mvpl-footer-fixed", lv.footer_fixed),
            ("style", f"{variables} {style}".strip()),
        ]
    )


@register.simple_tag(takes_context=True)
def sidebar_attrs(
    context,
    side="left",
    collapse=None,
    breakpoint=None,  # noqa: A002 - the option's name in the markup
    behavior=None,
    persist=None,
    closed=False,
    width=None,
    rail_width=None,
    css_class="",
):
    """Write the attributes of a sidebar's ``<aside>``.

    ``persist`` names the cookie its open or closed state is remembered under.
    The state is read from the request, so the template needs the ``request``
    context processor for a remembered state to be drawn.
    """
    sb = settle_sidebar(
        side,
        collapse=collapse,
        breakpoint=breakpoint,
        behavior=behavior,
        persist=persist,
        closed=closed,
        cookies=cookies_of(context),
    )
    style = " ".join(
        part
        for part in (
            f"--mvpl-w: {width};" if width else "",
            f"--mvpl-rail-w: {rail_width};" if rail_width else "",
        )
        if part
    )
    return write_attrs(
        [
            ("class", f"mvpl-sidebar {css_class}".strip()),
            ("data-side", sb.side),
            ("data-collapse", sb.collapse),
            ("data-breakpoint", sb.breakpoint),
            ("data-behavior", sb.behavior),
            ("data-state", sb.state),
            ("data-mvpl-rail", sb.rail),
            ("data-persist", persist or None),
            ("style", style or None),
        ]
    )
