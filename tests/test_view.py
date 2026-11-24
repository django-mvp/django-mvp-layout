"""Tests for the layout code parser."""

import itertools

import pytest

from mvp_layout.view import LayoutView, LayoutViewError

DEFAULT_CODE = "hHh lpr fFf"
HEADER_HEIGHT = "var(--mvpl-header-h, 0px)"
FOOTER_HEIGHT = "var(--mvpl-footer-h, 0px)"

# Each corner choice of the top row, spelled out by hand: the letters of the
# row, its areas, and whether the left and right sidebars sit beside the header
# (True) or reach the top (False).
TOP_ROWS = [
    ("hhh", "header header header", True, True),
    ("lhh", "left header header", False, True),
    ("hhr", "header header right", True, False),
    ("lhr", "left header right", False, False),
]
BOTTOM_ROWS = [
    ("fff", "footer footer footer", True, True),
    ("lff", "left footer footer", False, True),
    ("ffr", "footer footer right", True, False),
    ("lfr", "left footer right", False, False),
]
CORNERS = list(itertools.product(TOP_ROWS, BOTTOM_ROWS))

INVALID = [
    pytest.param("hHh lpr", id="two groups"),
    pytest.param("hHh lpr fFf extra", id="four groups"),
    pytest.param("hHhlprfFf", id="no spaces"),
    pytest.param("hHh lpr fFfx", id="too long"),
    pytest.param("xHh lpr fFf", id="wrong top-left letter"),
    pytest.param("hHx lpr fFf", id="wrong top-right letter"),
    pytest.param("hXh lpr fFf", id="wrong header letter"),
    pytest.param("hHh lpr xFf", id="wrong bottom-left letter"),
    pytest.param("hHh lpr fFx", id="wrong bottom-right letter"),
    pytest.param("hHh fFf lpr", id="rows out of order"),
    pytest.param("rHl lpr fFf", id="sides swapped in the top row"),
    pytest.param("hHh lpl fFf", id="wrong middle row"),
    pytest.param(42, id="integer"),
    pytest.param(["hHh", "lpr", "fFf"], id="list"),
    pytest.param(b"hHh lpr fFf", id="bytes"),
]


def corner_code(top, bottom, header="h", footer="f"):
    """Join a top row, a middle row and a bottom row into a layout code."""
    top_row = top[0] + header + top[2]
    bottom_row = bottom[0] + footer + bottom[2]
    return f"{top_row} lpr {bottom_row}"


class TestLayoutView:
    """The layout code read into the facts the markup and styles need."""

    @pytest.mark.parametrize("value", [None, ""], ids=["none", "empty string"])
    def test_no_code_is_the_default_code(self, value):
        view = LayoutView.parse(value)

        assert view.code == DEFAULT_CODE

    def test_spaces_only_is_the_default_code(self):
        assert LayoutView.parse("   ").code == DEFAULT_CODE

    def test_extra_spaces_collapse_and_the_code_is_normalised(self):
        view = LayoutView.parse("lHh   LpR  lff")

        assert view.code == "lHh LpR lff"
        assert view == LayoutView.parse("lHh LpR lff")

    def test_surrounding_whitespace_is_dropped(self):
        assert LayoutView.parse("  hHh lpr fFf\n").code == DEFAULT_CODE

    @pytest.mark.parametrize(("top", "bottom"), CORNERS)
    def test_every_corner_choice_gives_its_areas(self, top, bottom):
        view = LayoutView.parse(corner_code(top[0], bottom[0]))

        assert view.areas == f"'{top[1]}' 'left page right' '{bottom[1]}'"

    @pytest.mark.parametrize(("top", "bottom"), CORNERS)
    def test_every_corner_choice_gives_its_offsets_when_fixed(self, top, bottom):
        view = LayoutView.parse(corner_code(top[0], bottom[0], header="H", footer="F"))

        assert view.left_top == (HEADER_HEIGHT if top[2] else "0px")
        assert view.right_top == (HEADER_HEIGHT if top[3] else "0px")
        assert view.left_bottom == (FOOTER_HEIGHT if bottom[2] else "0px")
        assert view.right_bottom == (FOOTER_HEIGHT if bottom[3] else "0px")

    @pytest.mark.parametrize(("top", "bottom"), CORNERS)
    def test_a_header_and_footer_that_scroll_leave_no_offset(self, top, bottom):
        view = LayoutView.parse(corner_code(top[0], bottom[0]))

        assert (
            view.left_top,
            view.right_top,
            view.left_bottom,
            view.right_bottom,
        ) == ("0px",) * 4

    def test_upper_case_header_and_footer_letters_fix_them(self):
        fixed = LayoutView.parse("hHh lpr fFf")
        loose = LayoutView.parse("hhh lpr fff")

        assert (fixed.header_fixed, fixed.footer_fixed) == (True, True)
        assert (loose.header_fixed, loose.footer_fixed) == (False, False)

    def test_the_header_and_footer_are_fixed_independently(self):
        view = LayoutView.parse("hHh lpr fff")

        assert (view.header_fixed, view.footer_fixed) == (True, False)

    @pytest.mark.parametrize(
        "code",
        ["Lhh lpr fff", "hhh Lpr fff", "hhh lpr Lff"],
        ids=["top", "middle", "bottom"],
    )
    def test_a_left_sidebar_is_fixed_when_any_of_its_letters_is_upper_case(self, code):
        view = LayoutView.parse(code)

        assert view.left_fixed is True
        assert view.right_fixed is False

    @pytest.mark.parametrize(
        "code",
        ["hhR lpr fff", "hhh lpR fff", "hhh lpr ffR"],
        ids=["top", "middle", "bottom"],
    )
    def test_a_right_sidebar_is_fixed_when_any_of_its_letters_is_upper_case(self, code):
        view = LayoutView.parse(code)

        assert view.right_fixed is True
        assert view.left_fixed is False

    def test_sidebars_are_loose_when_no_letter_of_theirs_is_upper_case(self):
        view = LayoutView.parse("lHh lpr lFf")

        assert (view.left_fixed, view.right_fixed) == (False, False)

    @pytest.mark.parametrize("value", INVALID)
    def test_a_value_that_is_not_a_layout_code_is_refused(self, value):
        with pytest.raises(LayoutViewError) as refusal:
            LayoutView.parse(value)

        assert repr(value) in str(refusal.value)

    @pytest.mark.parametrize("value", INVALID)
    def test_the_refusal_states_the_rules(self, value):
        with pytest.raises(LayoutViewError) as refusal:
            LayoutView.parse(value)

        # The rules name the example code and every letter a corner may take.
        message = str(refusal.value)
        assert DEFAULT_CODE in message
        assert all(letter in message for letter in "hlrf")

    def test_the_refusal_is_a_value_error(self):
        assert issubclass(LayoutViewError, ValueError)

    def test_every_valid_combination_parses_to_a_view_of_its_own_code(self):
        # SC-002: all 16 corner choices, in each of the four fixed settings.
        codes = {
            corner_code(top[0], bottom[0], header, footer)
            for top, bottom in CORNERS
            for header, footer in itertools.product("hH", "fF")
        }

        assert len(codes) == 64
        assert {LayoutView.parse(code).code for code in codes} == codes
