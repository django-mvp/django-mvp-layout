"""Reading a layout code into grid areas and sticky offsets."""

import pytest

from mvp_layout.view import LayoutView, LayoutViewError


class TestParse:
    def test_the_rows_become_grid_template_areas(self) -> None:
        view = LayoutView.parse("lHh LpR lff")
        assert (
            view.areas == "'left header header' 'left page right' 'left footer footer'"
        )

    def test_no_code_reads_as_the_default(self) -> None:
        assert LayoutView.parse(None).code == LayoutView.DEFAULT
        assert LayoutView.parse("").code == LayoutView.DEFAULT

    def test_extra_whitespace_is_ignored(self) -> None:
        assert LayoutView.parse("  hHh   lpr\nfFf ").code == "hHh lpr fFf"

    @pytest.mark.parametrize(
        ("code", "fixed"),
        [
            ("hHh lpr fff", {"header"}),
            ("hhh Lpr fff", {"left"}),
            ("hhh lpR fff", {"right"}),
            ("hhh lpr fFf", {"footer"}),
            ("hhh lpr fff", set()),
        ],
    )
    def test_upper_case_fixes_that_area(self, code, fixed) -> None:
        view = LayoutView.parse(code)
        flags = {
            "header": view.header_fixed,
            "left": view.left_fixed,
            "right": view.right_fixed,
            "footer": view.footer_fixed,
        }
        assert {name for name, on in flags.items() if on} == fixed

    def test_an_upper_case_corner_fixes_the_sidebar_that_reaches_it(self) -> None:
        assert LayoutView.parse("Lhh lpr fff").left_fixed

    def test_a_fixed_sidebar_below_a_fixed_header_sticks_under_it(self) -> None:
        view = LayoutView.parse("hHh LpR fff")
        assert "--mvpl-header-h" in view.left_top
        assert "--mvpl-header-h" in view.right_top

    def test_a_sidebar_that_reaches_the_top_sticks_at_zero(self) -> None:
        view = LayoutView.parse("lHh Lpr fff")
        assert view.left_reaches_top
        assert "--mvpl-header-h" not in view.left_top

    @pytest.mark.parametrize(
        "code",
        [
            "hhh",
            "hhh lpr",
            "xhh lpr fff",
            "hhh rpl fff",
            "hhh lpr fhf",
            "lHhh LpR lff",
            42,
        ],
    )
    def test_a_wrong_code_is_refused(self, code) -> None:
        with pytest.raises(LayoutViewError):
            LayoutView.parse(code)
