"""The <c-layout> components, as rendered."""

import pytest


class TestLayout:
    def test_it_wraps_its_areas_in_the_grid(self, render) -> None:
        html = render(
            '<c-layout view="lHh LpR lff" id="app"><c-layout.page>Body</c-layout.page></c-layout>'
        )
        assert 'id="app"' in html
        assert 'class="mvpl-grid"' in html
        assert 'data-mvpl-view="lHh LpR lff"' in html
        assert "Body" in html

    def test_it_is_given_an_id_when_it_has_none(self, render) -> None:
        html = render("<c-layout><c-layout.page>Body</c-layout.page></c-layout>")
        assert 'id="layout-' in html

    def test_it_mounts_itself(self, render) -> None:
        html = render(
            '<c-layout id="app"><c-layout.page>Body</c-layout.page></c-layout>'
        )
        assert 'MvpLayout("app")' in html

    def test_a_wrong_code_raises(self, render) -> None:
        with pytest.raises(ValueError):
            render(
                '<c-layout view="nope"><c-layout.page>Body</c-layout.page></c-layout>'
            )


class TestAreas:
    @pytest.mark.parametrize(
        ("component", "css_class"),
        [("header", "mvpl-header"), ("page", "mvpl-page"), ("footer", "mvpl-footer")],
    )
    def test_each_area_carries_its_grid_class(
        self, render, component, css_class
    ) -> None:
        html = render(f"<c-layout.{component}>Inside</c-layout.{component}>")
        assert css_class in html
        assert "Inside" in html

    def test_the_page_tag_can_be_main(self, render) -> None:
        html = render('<c-layout.page tag="main">Inside</c-layout.page>')
        assert html.strip().startswith("<main")


class TestSidebar:
    def test_it_draws_its_content_in_a_panel(self, render) -> None:
        html = render(
            '<c-layout.sidebar side="right" label="Filters">Facets</c-layout.sidebar>'
        )
        assert 'data-side="right"' in html
        assert 'aria-label="Filters"' in html
        assert 'class="mvpl-panel">Facets' in html
        assert "data-mvpl-close" in html

    def test_an_empty_sidebar_is_not_drawn(self, render) -> None:
        assert "<aside" not in render(
            '<c-layout.sidebar side="right">  </c-layout.sidebar>'
        )

    def test_a_remembered_state_is_drawn(self, render) -> None:
        from django.test import RequestFactory

        request = RequestFactory().get("/")
        request.COOKIES["mvpl-nav"] = "closed"
        html = render(
            '<c-layout.sidebar persist="nav">Nav</c-layout.sidebar>', request=request
        )
        assert 'data-state="closed"' in html


class TestToggle:
    def test_it_names_its_sidebar(self, render) -> None:
        html = render('<c-layout.toggle side="right" />')
        assert 'data-mvpl-toggle="right"' in html
        assert 'aria-expanded="false"' in html

    def test_an_unknown_side_falls_back_to_left(self, render) -> None:
        assert 'data-mvpl-toggle="left"' in render('<c-layout.toggle side="up" />')

    def test_when_is_passed_to_the_script(self, render) -> None:
        assert 'data-mvpl-when="closed"' in render('<c-layout.toggle when="closed" />')
