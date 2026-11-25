"""The demo project's pages."""

from pathlib import Path

from django.conf import settings
from django.views.generic import TemplateView

from mvp_layout.view import LayoutView, LayoutViewError

# The base template the docs give for a project without django-cotton. The demo
# renders the file itself, so the docs can't show one the demo doesn't run.
EXAMPLE_BASE = Path(settings.BASE_DIR) / "docs" / "examples" / "base.html"

EXAMPLES = [
    ("lHh LpR lff", "This site's own layout"),
    ("hHh LpR fFf", "Header and footer stay"),
    ("hHh lpr fff", "Only the header stays"),
    ("hhh lpr fff", "Nothing stays"),
    ("lHr LpR lfr", "Both sidebars full height"),
    ("hHh LpR fff", "Footer across the bottom"),
]
COLLAPSES = [
    ("offcanvas", "Slides away"),
    ("icons", "Icon rail"),
    ("none", "Stays open"),
]
BREAKPOINTS = [
    ("sm", "sm · 40rem"),
    ("md", "md · 48rem"),
    ("lg", "lg · 64rem"),
    ("xl", "xl · 80rem"),
    ("2xl", "2xl · 96rem"),
]
BEHAVIORS = [
    ("auto", "By breakpoint"),
    ("docked", "Always beside"),
    ("overlay", "Always a drawer"),
]
DEFAULTS = {
    "left": {"collapse": "icons", "breakpoint": "md", "behavior": "auto"},
    "right": {"collapse": "offcanvas", "breakpoint": "lg", "behavior": "auto"},
}


def pick(value, choices, default):
    """Return the value when it is one of the choices, else the default."""
    return value if value in {key for key, _ in choices} else default


def sidebar_options(params, side):
    """One sidebar's options from the query string."""
    defaults = DEFAULTS[side]
    return {
        "collapse": pick(
            params.get(f"{side}_collapse"), COLLAPSES, defaults["collapse"]
        ),
        "breakpoint": pick(
            params.get(f"{side}_breakpoint"), BREAKPOINTS, defaults["breakpoint"]
        ),
        "behavior": pick(
            params.get(f"{side}_behavior"), BEHAVIORS, defaults["behavior"]
        ),
    }


def plain_snippet(code, left, right):
    """Write the same layout as a template that doesn't use django-cotton."""

    def sidebar(side, opts):
        return (
            f'    <aside {{% sidebar_attrs "{side}" collapse="{opts["collapse"]}" '
            f'breakpoint="{opts["breakpoint"]}" '
            f'behavior="{opts["behavior"]}" %}} aria-label="…">\n'
            '      <div class="mvpl-backdrop" data-mvpl-close '
            'aria-hidden="true"></div>\n'
            '      <div class="mvpl-panel">…</div>\n'
            "    </aside>\n"
        )

    return (
        "{% load mvp_layout %}\n"
        f'<div id="app" {{% layout_attrs "{code}" %}}>\n'
        '  <div class="mvpl-grid">\n'
        '    <header class="mvpl-header">\n'
        '      <button type="button" class="mvpl-toggle" data-mvpl-toggle="left" '
        'aria-label="Navigation">…</button>\n'
        "    </header>\n"
        + sidebar("left", left)
        + '    <main class="mvpl-page">…</main>\n'
        + sidebar("right", right)
        + '    <footer class="mvpl-footer">…</footer>\n'
        "  </div>\n"
        "</div>"
    )


def markup_snippet(code, left, right):
    """Write the same layout as components."""

    def sidebar(side, opts):
        return (
            f'  <c-layout.sidebar side="{side}" collapse="{opts["collapse"]}" '
            f'breakpoint="{opts["breakpoint"]}" behavior="{opts["behavior"]}">\n'
            "    …\n"
            "  </c-layout.sidebar>\n"
        )

    return (
        f'<c-layout view="{code}" container style="height: 32rem">\n'
        "  <c-layout.header>\n"
        '    <c-layout.toggle side="left" /> … <c-layout.toggle side="right" />\n'
        "  </c-layout.header>\n"
        + sidebar("left", left)
        + "  <c-layout.page>…</c-layout.page>\n"
        + sidebar("right", right)
        + "  <c-layout.footer>…</c-layout.footer>\n"
        "</c-layout>"
    )


BREAKPOINT_WIDTHS = dict(
    sm="40rem", md="48rem", lg="64rem", xl="80rem", **{"2xl": "96rem"}
)


def describe(side, opts):
    """One sentence on how a sidebar opens and closes."""
    name = f"The {side} sidebar"
    if opts["behavior"] == "overlay":
        return f"{name} is a drawer over the page at every width."
    closes = {
        "offcanvas": "slides away when closed",
        "icons": "shrinks to an icon rail when closed",
        "none": "stays open, with no toggle",
    }[opts["collapse"]]
    if opts["behavior"] == "docked":
        return f"{name} {closes}, and stays beside the page at every width."
    width = BREAKPOINT_WIDTHS[opts["breakpoint"]]
    return (
        f"{name} {closes}. Below {width} of layout width it is a drawer over the page."
    )


def describe_reach(side, top, bottom):
    """Say which of the header and the footer a sidebar runs beside.

    Args:
        side: ``left`` or ``right``.
        top: Whether the code gives the sidebar the top corner.
        bottom: Whether the code gives the sidebar the bottom corner.

    Returns:
        One sentence.
    """
    name = f"The {side} sidebar"
    if top and bottom:
        return f"{name} runs the full height, beside the header and the footer."
    if top:
        return f"{name} reaches the top, beside the header."
    if bottom:
        return f"{name} reaches the bottom, beside the footer."
    return f"{name} sits between the header and the footer."


def explain(view):
    """Say in plain sentences what a layout code does.

    Args:
        view: The parsed layout code.

    Returns:
        The sentences, one for each sidebar and one for what stays in place.
    """
    top, _, bottom = view.code.split(" ")
    lines = [
        describe_reach("left", top[0] == "l", bottom[0] == "l"),
        describe_reach("right", top[2] == "r", bottom[2] == "r"),
    ]
    fixed = [
        name
        for name, flag in (
            ("the header", view.header_fixed),
            ("the left sidebar", view.left_fixed),
            ("the right sidebar", view.right_fixed),
            ("the footer", view.footer_fixed),
        )
        if flag
    ]
    if not fixed:
        return [*lines, "Everything scrolls with the page."]
    joined = (
        fixed[0] if len(fixed) == 1 else ", ".join(fixed[:-1]) + " and " + fixed[-1]
    )
    verb = "stays" if len(fixed) == 1 else "stay"
    return [*lines, f"While the page scrolls, {joined} {verb} in place."]


def preview_context(params):
    """Everything the preview needs, including the refusal for a wrong code."""
    code = params.get("view", EXAMPLES[0][0])
    left = sidebar_options(params, "left")
    right = sidebar_options(params, "right")
    try:
        view = LayoutView.parse(code)
        error = ""
    except LayoutViewError as exc:
        view = None
        error = str(exc)
    return {
        "code": code,
        "view": view,
        "error": error,
        "left": left,
        "right": right,
        "plain_snippet": plain_snippet(view.code, left, right) if view else "",
        "markup_snippet": markup_snippet(view.code, left, right) if view else "",
        "sides": [("left", left), ("right", right)],
        "explanation": explain(view) if view else [],
        "left_description": describe("left", left),
        "right_description": describe("right", right),
        "examples": EXAMPLES,
        "collapses": COLLAPSES,
        "breakpoints": BREAKPOINTS,
        "behaviors": BEHAVIORS,
        "paragraphs": range(14),
        "nav": [
            ("house", "Home"),
            ("inbox", "Inbox"),
            ("file-text", "Documents"),
            ("chat", "Discussions"),
            ("star", "Starred"),
            ("gear", "Settings"),
        ],
    }


class HomeView(TemplateView):
    """What the package does, on a page laid out by it."""

    template_name = "demo/home.html"


class PlaygroundView(TemplateView):
    """Type a code, set the sidebars, see the layout."""

    template_name = "demo/playground.html"

    def get_template_names(self):
        """Return the preview template when the page script asks for it."""
        # The page's script asks for the parts that change and swaps them in.
        if self.request.headers.get("X-Preview"):
            return ["demo/preview.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        """Add the settings the page is drawn with."""
        context = super().get_context_data(**kwargs)
        context.update(preview_context(self.request.GET))
        # The preview gets the page's full width, so its Full setting is wider
        # than 1024. The reference starts closed and remembers its own state.
        context.update(
            page_width="max-w-none", aside_persist="demo-reference", aside_closed=True
        )
        return context


class NestedView(TemplateView):
    """Layouts inside a card, a dialog and each other."""

    template_name = "demo/nested.html"

    def get_context_data(self, **kwargs):
        """Add the settings the page is drawn with."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "folders": [
                    ("inbox", "Inbox", 12),
                    ("star", "Starred", 3),
                    ("send", "Sent", 0),
                    ("file-earmark", "Drafts", 2),
                    ("archive", "Archive", 0),
                    ("trash", "Bin", 0),
                ],
                "mail": [
                    (
                        "Ana Ruiz",
                        "Field season schedule",
                        "The boats are booked for the second week of June, "
                        "weather permitting.",
                        "09:14",
                        True,
                    ),
                    (
                        "Kofi Mensah",
                        "Re: core samples",
                        "I've logged the last six cores. Two need re-labelling "
                        "before they go to the lab.",
                        "08:52",
                        True,
                    ),
                    (
                        "Lena Vogt",
                        "Budget for the spring workshop",
                        "Attached is the draft. The catering line is still "
                        "an estimate.",
                        "Yesterday",
                        False,
                    ),
                    (
                        "Sam Patel",
                        "Instrument calibration",
                        "The thermistor string reads 0.2 °C high at depth. "
                        "Logged in the notes.",
                        "Yesterday",
                        False,
                    ),
                    (
                        "Mia Chen",
                        "Paper draft, section 3",
                        "I rewrote the methods to match the new sampling grid.",
                        "Mon",
                        False,
                    ),
                    (
                        "Jonas Berg",
                        "Shared drive tidy-up",
                        "Old exports moved to the archive folder, nothing deleted.",
                        "Mon",
                        False,
                    ),
                    (
                        "Ana Ruiz",
                        "Permits",
                        "The coastal permit came through. Copy is in the shared drive.",
                        "Sun",
                        False,
                    ),
                    (
                        "Priya Nair",
                        "Seminar on Thursday",
                        "Room changed to 2.14, same time.",
                        "Sat",
                        False,
                    ),
                    (
                        "Tom Ellis",
                        "Data release",
                        "The DOI is minted. Release notes need one more read.",
                        "Fri",
                        False,
                    ),
                    (
                        "Kofi Mensah",
                        "Lab booking",
                        "We have the cold room from Tuesday to Friday.",
                        "Fri",
                        False,
                    ),
                ],
                "settings_sections": [
                    ("person", "Profile"),
                    ("bell", "Notifications"),
                    ("shield-lock", "Privacy"),
                    ("palette", "Appearance"),
                    ("key", "Access keys"),
                ],
                "projects": [
                    ("folder", "Coastal survey"),
                    ("folder", "Spring workshop"),
                    ("folder", "Data release 2026"),
                ],
                "documents": [
                    "Overview",
                    "Methods",
                    "Sampling grid",
                    "Results",
                    "Open questions",
                ],
                "comments": [
                    ("Mia Chen", "Should the grid spacing go in a table?"),
                    ("Kofi Mensah", "Core 14 is missing from the list."),
                    ("Lena Vogt", "Cite the 2024 calibration report here."),
                ],
                "products": [
                    ("Sediment corer", "Field", "€1,240"),
                    ("Thermistor string", "Sensors", "€860"),
                    ("Sample bags, 500", "Consumables", "€48"),
                    ("Handheld GPS", "Field", "€310"),
                    ("Conductivity probe", "Sensors", "€540"),
                    ("Cool box, 40 l", "Field", "€95"),
                ],
                "paragraphs": range(6),
            }
        )
        return context


class PlainView(TemplateView):
    """A page whose base template is written without django-cotton."""

    template_name = "demo/plain.html"

    def get_context_data(self, **kwargs):
        """Add the settings the page is drawn with."""
        context = super().get_context_data(**kwargs)
        context["base_source"] = EXAMPLE_BASE.read_text()
        return context


SIDEBAR_CODES = [
    ("HbF", "Header and footer stay"),
    ("Hbf", "Only the header stays"),
    ("hbF", "Only the footer stays"),
    ("hbf", "Nothing stays"),
]
SIDEBAR_PARTS = [("header", "Header"), ("body", "Body"), ("footer", "Footer")]
SIDEBAR_NAV = [
    ("house", "Home"),
    ("inbox", "Inbox"),
    ("send", "Sent"),
    ("file-text", "Documents"),
    ("folder", "Projects"),
    ("chat", "Discussions"),
    ("star", "Starred"),
    ("archive", "Archive"),
    ("trash", "Trash"),
    ("bell", "Notifications"),
    ("search", "Search"),
    ("funnel", "Filters"),
    ("layers", "Collections"),
    ("palette", "Appearance"),
    ("key", "Access keys"),
    ("shield-lock", "Security"),
    ("gear", "Settings"),
]


def sidebar_snippet(code, parts, opts):
    """The preview's sidebar as components, with its content left out."""
    attrs = f'side="left" view="{code}"'
    for key, default in (("collapse", "offcanvas"), ("breakpoint", "lg")):
        if opts[key] != default:
            attrs += f' {key}="{opts[key]}"'
    if opts["behavior"] != "auto":
        attrs += f' behavior="{opts["behavior"]}"'
    lines = [f"<c-layout.sidebar {attrs}>"]
    for part in parts:
        lines.append(f"  <c-layout.{part}>…</c-layout.{part}>")
    lines.append("</c-layout.sidebar>")
    return "\n".join(lines)


class SidebarBehaviorView(TemplateView):
    """Set one sidebar's header, body and footer and how it opens, and see it."""

    template_name = "demo/sidebar_behavior.html"

    def get_context_data(self, **kwargs):
        """Add the settings the preview is drawn with."""
        context = super().get_context_data(**kwargs)
        params = self.request.GET
        code = pick(params.get("view"), SIDEBAR_CODES, SIDEBAR_CODES[0][0])
        # A form sent with every box unticked still carries "set", so it isn't
        # read as a first visit.
        if params.get("set"):
            chosen = params.getlist("parts")
            parts = [key for key, _ in SIDEBAR_PARTS if key in chosen]
        else:
            parts = [key for key, _ in SIDEBAR_PARTS]
        opts = sidebar_options(params, "left")
        context.update(
            code=code,
            codes=SIDEBAR_CODES,
            parts=parts,
            part_choices=SIDEBAR_PARTS,
            opts=opts,
            collapses=COLLAPSES,
            breakpoints=BREAKPOINTS,
            behaviors=BEHAVIORS,
            nav=SIDEBAR_NAV,
            snippet=sidebar_snippet(code, parts, opts),
            page_width="max-w-none",
        )
        return context
