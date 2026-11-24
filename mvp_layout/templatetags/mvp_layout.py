"""Template tags that write a layout's attributes.

A template calls them on the elements of a layout::

    {% load mvp_layout %}
    <div {% layout_attrs "lHh LpR lff" %}>
      <div class="mvpl-grid">
        <header class="mvpl-header">…</header>
        <aside {% sidebar_attrs "left" persist="nav" %}
               aria-label="Navigation">…</aside>
        <main class="mvpl-page">…</main>
      </div>
    </div>
"""

import re
import uuid
from dataclasses import dataclass
from typing import ClassVar, Self

from django import template
from django.http import HttpRequest
from django.utils.html import format_html, format_html_join
from django.utils.safestring import SafeString

from mvp_layout.view import LayoutView

register = template.Library()


class LayoutOptionError(ValueError):
    """A sidebar option that is not one of its choices."""


@dataclass(frozen=True)
class Sidebar:
    """A sidebar's options, settled, and the state the server draws it in.

    ``left`` and ``right`` name the reading-start and reading-end sides, so in a
    right-to-left page the left sidebar is drawn at the right.
    """

    SIDES: ClassVar[tuple[str, ...]] = ("left", "right")
    COLLAPSES: ClassVar[tuple[str, ...]] = ("offcanvas", "icons", "none")
    BEHAVIORS: ClassVar[tuple[str, ...]] = ("auto", "docked", "overlay")
    BREAKPOINTS: ClassVar[tuple[str, ...]] = ("sm", "md", "lg", "xl", "2xl")
    DEFAULT_BREAKPOINTS: ClassVar[dict[str, str]] = {"left": "lg", "right": "xl"}
    STATES: ClassVar[tuple[str, ...]] = ("open", "closed")
    COOKIE_PREFIX: ClassVar[str] = "mvpl-"
    PERSIST_NAME: ClassVar[re.Pattern[str]] = re.compile(r"[A-Za-z0-9_-]+")

    side: str
    collapse: str
    behavior: str
    breakpoint: str
    state: str

    @property
    def rail(self) -> bool:
        """Whether the sidebar is closed to its icon rail beside the page."""
        return (
            self.state == "closed"
            and self.collapse == "icons"
            and self.behavior != "overlay"
        )

    @staticmethod
    def choose(name: str, value: object, choices: tuple[str, ...], default: str) -> str:
        """Check an option against its choices.

        Args:
            name: The option's name, for the message.
            value: The value given. ``None`` and an empty string mean none given.
            choices: The values the option allows.
            default: The value used when none was given.

        Returns:
            The value, or the default when none was given.

        Raises:
            LayoutOptionError: The value is not one of the choices.
        """
        if value in (None, ""):
            return default
        if value not in choices:
            allowed = ", ".join(choices)
            raise LayoutOptionError(
                f"{value!r} is not a sidebar {name}. Choose one of: {allowed}."
            )
        return str(value)

    @classmethod
    def settle(
        cls,
        side: object = None,
        *,
        collapse: object = None,
        breakpoint: object = None,  # noqa: A002 - the option's name in the markup
        behavior: object = None,
        persist: object = None,
        closed: object = False,
        request: HttpRequest | None = None,
    ) -> Self:
        """Settle a sidebar's options and read the state its reader left it in.

        The state comes from the ``mvpl-<persist>`` cookie the layout script
        writes, so a sidebar the reader closed is drawn closed and never opens
        and snaps shut on load. A sidebar with ``collapse="none"`` is always open.

        Args:
            side: ``left`` or ``right``. Defaults to ``left``.
            collapse: ``offcanvas``, ``icons`` or ``none``. Defaults to ``offcanvas``.
            breakpoint: ``sm``, ``md``, ``lg``, ``xl`` or ``2xl``. Defaults to
                ``lg`` for the left sidebar and ``xl`` for the right.
            behavior: ``auto``, ``docked`` or ``overlay``. Defaults to ``auto``.
            persist: The name the state is remembered under. Without one, or with an
                empty one, nothing is remembered.
            closed: ``True`` draws the sidebar closed unless the cookie says
                otherwise. Any value but ``True`` leaves it open.
            request: The request whose cookies are read. Without one the state
                is the one the options give.

        Returns:
            The settled options and state.

        Raises:
            LayoutOptionError: An option is outside its choices, or the persist
                name has characters other than ``A-Za-z0-9_-``.
        """
        side = cls.choose("side", side, cls.SIDES, "left")
        collapse = cls.choose("collapse", collapse, cls.COLLAPSES, "offcanvas")
        behavior = cls.choose("behavior", behavior, cls.BEHAVIORS, "auto")
        breakpoint = cls.choose(  # noqa: A001
            "breakpoint", breakpoint, cls.BREAKPOINTS, cls.DEFAULT_BREAKPOINTS[side]
        )
        if persist not in (None, "") and not cls.PERSIST_NAME.fullmatch(str(persist)):
            raise LayoutOptionError(
                f"{persist!r} is not a sidebar persist name. Use only the characters"
                " A-Za-z0-9_-, as it becomes part of a cookie name."
            )
        state = "closed" if closed is True else "open"
        if persist and request is not None:
            remembered = request.COOKIES.get(cls.COOKIE_PREFIX + str(persist))
            if remembered in cls.STATES:
                state = remembered
        if collapse == "none":
            state = "open"
        return cls(side, collapse, behavior, breakpoint, state)


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
def layout_uid(prefix):
    """Return an id for an element that was not given one.

    Args:
        prefix: What the id starts with, such as ``layout`` or ``sidebar``.

    Returns:
        The prefix, a dash and twelve random hexadecimal characters.
    """
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


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
    style="",
):
    """Write the attributes of a sidebar's ``<aside>``.

    ``persist`` names the cookie its open or closed state is remembered under.
    The state is read from the request, so the template needs the ``request``
    context processor for a remembered state to be drawn.

    Args:
        context: The template context, which carries the request.
        side: ``left`` or ``right``, the reading-start or reading-end side.
        collapse: ``offcanvas``, ``icons`` or ``none``.
        breakpoint: ``sm``, ``md``, ``lg``, ``xl`` or ``2xl``, the layout width
            below which the sidebar is a drawer.
        behavior: ``auto``, ``docked`` or ``overlay``.
        persist: The name the sidebar's state is remembered under.
        closed: ``True`` or ``False``, whether the sidebar starts closed.
        width: The sidebar's width, as a CSS length.
        rail_width: The width of its icon rail, as a CSS length.
        css_class: Classes added to the sidebar's own.
        style: Declarations added after the sidebar's own.

    Returns:
        The attributes, ready to place inside a tag.

    Raises:
        LayoutOptionError: An option is outside its choices.
    """
    sidebar = Sidebar.settle(
        side,
        collapse=collapse,
        breakpoint=breakpoint,
        behavior=behavior,
        persist=persist,
        closed=closed,
        request=context.get("request"),
    )
    style = " ".join(
        part
        for part in (
            f"--mvpl-w: {width};" if width else "",
            f"--mvpl-rail-w: {rail_width};" if rail_width else "",
            style.strip(),
        )
        if part
    )
    return write_attrs(
        [
            ("class", f"mvpl-sidebar {css_class}".strip()),
            ("data-mvpl-side", sidebar.side),
            ("data-mvpl-collapse", sidebar.collapse),
            ("data-mvpl-breakpoint", sidebar.breakpoint),
            ("data-mvpl-behavior", sidebar.behavior),
            ("data-mvpl-state", sidebar.state),
            ("data-mvpl-rail", sidebar.rail),
            ("data-mvpl-persist", persist or None),
            ("style", style or None),
        ]
    )
