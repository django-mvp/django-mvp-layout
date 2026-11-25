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
    ("hHh LpR fFf", "Sticky header and footer"),
    ("hHh lpr fff", "Sticky header"),
    ("hhh lpr fff", "Nothing sticks"),
    ("lHr LpR lfr", "Both sidebars full height"),
    ("hHh LpR fff", "Full-width footer"),
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
SIDEBAR_VIEWS = [
    ("", "Not set"),
    ("HbF", "Sticky header and footer"),
    ("Hbf", "Sticky header"),
    ("hbF", "Sticky footer"),
    ("hbf", "Nothing sticks"),
]
PARTS = [("header", "Header"), ("body", "Body"), ("footer", "Footer")]
DEFAULTS = {
    "left": {
        "collapse": "icons",
        "breakpoint": "md",
        "behavior": "auto",
        "view": "HbF",
    },
    "right": {
        "collapse": "offcanvas",
        "breakpoint": "lg",
        "behavior": "auto",
        "view": "",
    },
}


def pick(value, choices, default):
    """Return the value when it is one of the choices, else the default."""
    return value if value in {key for key, _ in choices} else default


def sidebar_options(params, side):
    """One sidebar's options from the query string."""
    defaults = DEFAULTS[side]
    # The form always sends the layout code, so a query without it is a first
    # visit, and a sent form with every part unticked means no parts.
    if "view" in params:
        chosen = params.getlist(f"{side}_parts")
        parts = [key for key, _ in PARTS if key in chosen]
    else:
        parts = [key for key, _ in PARTS]
    return {
        "view": pick(params.get(f"{side}_view"), SIDEBAR_VIEWS, defaults["view"]),
        "parts": parts,
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


PART_TAGS = {"header": "header", "body": "div", "footer": "footer"}


def plain_snippet(code, left, right):
    """Write the same layout as a template that doesn't use django-cotton."""

    def sidebar(side, opts):
        if opts["view"]:
            panel = (
                f'      <div class="mvpl-panel {opts["view"]}">\n'
                + "".join(
                    f'        <{PART_TAGS[part]} class="mvpl-{part}">…'
                    f"</{PART_TAGS[part]}>\n"
                    for part in opts["parts"]
                )
                + "      </div>\n"
            )
        else:
            panel = '      <div class="mvpl-panel">…</div>\n'
        return (
            f'    <aside {{% sidebar_attrs "{side}" collapse="{opts["collapse"]}" '
            f'breakpoint="{opts["breakpoint"]}" '
            f'behavior="{opts["behavior"]}" %}} aria-label="…">\n'
            '      <div class="mvpl-backdrop" data-mvpl-close '
            'aria-hidden="true"></div>\n'
            + panel
            + "    </aside>\n"
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
        view = f' view="{opts["view"]}"' if opts["view"] else ""
        if opts["view"]:
            inside = "".join(
                f"    <c-layout.{part}>…</c-layout.{part}>\n" for part in opts["parts"]
            )
        else:
            inside = "    …\n"
        return (
            f'  <c-layout.sidebar side="{side}" collapse="{opts["collapse"]}" '
            f'breakpoint="{opts["breakpoint"]}" behavior="{opts["behavior"]}"'
            f"{view}>\n" + inside + "  </c-layout.sidebar>\n"
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
    """Say how a sidebar opens and closes, and which of its parts are sticky."""
    sentence = describe_closing(side, opts)
    view = opts["view"]
    if not view:
        return sentence
    stays = [
        name
        for name, flag in (("header", view[0] == "H"), ("footer", view[2] == "F"))
        if flag and name in opts["parts"]
    ]
    if not stays:
        return f"{sentence} Nothing in it sticks."
    verb = "is" if len(stays) == 1 else "are"
    return f"{sentence} Its {' and '.join(stays)} {verb} sticky."


def describe_closing(side, opts):
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
        The sentences, one for each sidebar and one for what is sticky.
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
        return [*lines, "Nothing sticks."]
    joined = (
        fixed[0] if len(fixed) == 1 else ", ".join(fixed[:-1]) + " and " + fixed[-1]
    )
    verb = "is" if len(fixed) == 1 else "are"
    return [*lines, f"{joined[0].upper()}{joined[1:]} {verb} sticky."]


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
        "preset_match": code in {example for example, _ in EXAMPLES},
        "collapses": COLLAPSES,
        "breakpoints": BREAKPOINTS,
        "behaviors": BEHAVIORS,
        "sidebar_views": SIDEBAR_VIEWS,
        "parts": PARTS,
        "paragraphs": range(14),
        "nav": [
            ("house", "Home"),
            ("inbox", "Inbox"),
            ("file-text", "Documents"),
            ("chat", "Discussions"),
            ("star", "Starred"),
            ("send", "Sent"),
            ("folder", "Projects"),
            ("archive", "Archive"),
            ("trash", "Trash"),
            ("bell", "Notifications"),
            ("layers", "Collections"),
            ("palette", "Appearance"),
            ("key", "Access keys"),
            ("shield-lock", "Security"),
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
        # than 1024.
        context.update(page_width="max-w-none")
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

