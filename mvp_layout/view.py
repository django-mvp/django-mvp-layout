"""The layout code, such as ``lHh LpR lff``, read into what the templates need.

Three groups of three letters are the top, middle and bottom rows of the
layout, each read left, centre and right:

========  ================================
Letter    Area
========  ================================
``h``     the header
``l``     the left sidebar
``p``     the page
``r``     the right sidebar
``f``     the footer
========  ================================

A corner names the area that reaches it. An upper-case header, sidebar or
footer letter keeps that area in place while the layout scrolls. The rules are
Quasar's ``QLayout`` ``view`` property, and sphinx-daisyui reads its own
``layout`` option the same way.

Left and right name the reading-start and reading-end sides, so in a
right-to-left page the left sidebar is drawn at the right.
"""

import re
from dataclasses import dataclass
from typing import ClassVar

from django.utils.safestring import mark_safe

AREA_NAMES = {
    "h": "header",
    "l": "left",
    "p": "page",
    "r": "right",
    "f": "footer",
}
SHAPE = re.compile(r"^[hl]h[hr] lpr [fl]f[fr]$")
HEADER_HEIGHT = "var(--mvpl-header-h, 0px)"
FOOTER_HEIGHT = "var(--mvpl-footer-h, 0px)"


class LayoutViewError(ValueError):
    """A value that is not a layout code."""


@dataclass(frozen=True)
class LayoutView:
    """A layout code read into the facts the layout's markup and styles need."""

    DEFAULT: ClassVar[str] = "hHh lpr fFf"

    code: str
    areas: str
    header_fixed: bool
    left_fixed: bool
    right_fixed: bool
    footer_fixed: bool
    left_top: str
    left_bottom: str
    right_top: str
    right_bottom: str

    @classmethod
    def parse(cls, value: object) -> "LayoutView":
        """Read a layout code.

        Args:
            value: The layout code. ``None`` or an empty string gives the default
                code, and runs of spaces collapse to one.

        Returns:
            The code and what the layout's markup and styles read from it.

        Raises:
            LayoutViewError: The value is not a string, or not a layout code.
        """
        if value is None or value == "":
            value = cls.DEFAULT
        if not isinstance(value, str):
            raise LayoutViewError(cls.refusal(value))
        code = " ".join(value.split()) or cls.DEFAULT
        if not SHAPE.match(code.lower()):
            raise LayoutViewError(cls.refusal(value))
        rows = code.split(" ")
        lower = [row.lower() for row in rows]
        header_fixed = rows[0][1] == "H"
        footer_fixed = rows[2][1] == "F"
        left_fixed = "L" in (rows[0][0], rows[1][0], rows[2][0])
        right_fixed = "R" in (rows[0][2], rows[1][2], rows[2][2])
        return cls(
            code=code,
            areas=mark_safe(cls.template_areas(lower)),  # noqa: S308 - letters only
            header_fixed=header_fixed,
            left_fixed=left_fixed,
            right_fixed=right_fixed,
            footer_fixed=footer_fixed,
            left_top=HEADER_HEIGHT if header_fixed and lower[0][0] == "h" else "0px",
            left_bottom=FOOTER_HEIGHT if footer_fixed and lower[2][0] == "f" else "0px",
            right_top=HEADER_HEIGHT if header_fixed and lower[0][2] == "h" else "0px",
            right_bottom=FOOTER_HEIGHT
            if footer_fixed and lower[2][2] == "f"
            else "0px",
        )

    @staticmethod
    def template_areas(rows: list[str]) -> str:
        """Write rows of area letters as a ``grid-template-areas`` value.

        Args:
            rows: The three rows of the code, in lower case.

        Returns:
            The rows as quoted lists of area names.
        """
        return " ".join(
            "'" + " ".join(AREA_NAMES[letter] for letter in row) + "'" for row in rows
        )

    @staticmethod
    def refusal(value: object) -> str:
        """Write the message for a value that is not a layout code.

        Args:
            value: The value that was refused.

        Returns:
            A message that shows the value and states the rules.
        """
        return (
            f"{value!r} is not a layout code. A layout code is three groups of three "
            "letters separated by spaces, such as 'hHh lpr fFf'. The top row is h or l, "
            "then h, then h or r. The middle row is l, p, r. The bottom row is f or l, "
            "then f, then f or r. An upper-case letter keeps that area in place while "
            "the layout scrolls."
        )
