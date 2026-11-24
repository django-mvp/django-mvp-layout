"""The demo project's pages, asserted as rendered."""

# Everything in the demo fails quietly: a component Cotton cannot resolve
# renders as nothing and a template tag from a library that is not loaded is an
# error only when it is reached, so the pages are asserted by the layouts they
# draw rather than by their status.

import pytest
from django.urls import reverse

from demo.views import describe_reach, explain
from mvp_layout.view import LayoutView
from tests.conftest import elements_of

# Each page and the layouts it draws: the shell, then the playground's preview and
# the nested page's inbox, settings dialog, project, document and filters layouts.
LAYOUTS = {"home": 1, "playground": 2, "nested": 6, "plain": 1}

PHONE = {"width": 390, "height": 800}
DESKTOP = {"width": 1440, "height": 900}


def layouts_in(html: str) -> list[dict[str, str | None]]:
    """Return the attributes of each layout the page draws."""
    return [
        attrs
        for _, attrs in elements_of(html)
        if "data-mvpl" in attrs and "data-mvpl-side" not in attrs
    ]


def sidebars_in(html: str) -> dict[str, dict[str, str | None]]:
    """Return the attributes of each sidebar the page draws, by side."""
    return {
        attrs["data-mvpl-side"]: attrs
        for _, attrs in elements_of(html)
        if "data-mvpl-side" in attrs
    }


@pytest.mark.django_db
class TestPages:
    @pytest.mark.parametrize("name", LAYOUTS)
    def test_a_page_draws_its_layouts(self, client, name: str) -> None:
        response = client.get(reverse(name))

        assert response.status_code == 200
        assert len(layouts_in(response.content.decode())) == LAYOUTS[name]

    @pytest.mark.parametrize("name", LAYOUTS)
    def test_no_id_repeats(self, client, name: str) -> None:
        html = client.get(reverse(name)).content.decode()
        ids = [attrs["id"] for _, attrs in elements_of(html) if "id" in attrs]

        assert len(ids) == len(set(ids))

    @pytest.mark.parametrize("name", ["home", "playground", "nested"])
    def test_the_navigation_links_every_page(self, client, name: str) -> None:
        html = client.get(reverse(name)).content.decode()
        links = {attrs["href"] for tag, attrs in elements_of(html) if tag == "a"}

        assert {reverse(page) for page in LAYOUTS} <= links

    def test_the_plain_page_is_written_without_components(self, client) -> None:
        html = client.get(reverse("plain")).content.decode()

        # Its layout comes from the template tags in the documented base template.
        assert layouts_in(html)[0]["data-mvpl-view"] == "hHh LpR fFf"


@pytest.mark.django_db
class TestPlayground:
    def test_the_options_in_the_address_reach_the_preview_sidebars(
        self, client
    ) -> None:
        # The fragment holds the preview alone, so the page's own sidebars
        # cannot stand in for its.
        response = client.get(
            reverse("playground"),
            {"left_collapse": "none", "right_behavior": "overlay"},
            headers={"X-Preview": "1"},
        )

        sidebars = sidebars_in(response.content.decode())
        assert sidebars["left"]["data-mvpl-collapse"] == "none"
        assert sidebars["right"]["data-mvpl-behavior"] == "overlay"

    def test_a_wrong_code_draws_no_preview(self, client) -> None:
        response = client.get(reverse("playground"), {"view": "not a code"})

        ids = {attrs.get("id") for _, attrs in elements_of(response.content.decode())}
        assert response.status_code == 200
        assert "lp-layout" not in ids

    def test_the_page_script_gets_only_the_parts_that_change(self, client) -> None:
        response = client.get(
            reverse("playground"), {"view": "hhh lpr fff"}, headers={"X-Preview": "1"}
        )

        ids = {attrs.get("id") for _, attrs in elements_of(response.content.decode())}
        assert {"lp-layout", "lp-details"} <= ids
        assert "lp-form" not in ids


class TestExplanation:
    def test_each_combination_of_corners_is_told_apart(self) -> None:
        sentences = {
            describe_reach("left", top, bottom)
            for top in (True, False)
            for bottom in (True, False)
        }

        assert len(sentences) == 4

    @pytest.mark.parametrize(
        ("code", "held"),
        [
            ("hhh lpr fff", []),
            ("hHh lpr fff", ["header"]),
            ("hHh LpR fFf", ["header", "left sidebar", "right sidebar", "footer"]),
        ],
    )
    def test_it_names_each_area_that_stays_in_place(
        self, code: str, held: list[str]
    ) -> None:
        sentence = explain(LayoutView.parse(code))[-1]

        assert [
            area
            for area in ("header", "left sidebar", "right sidebar", "footer")
            if area in sentence
        ] == held


@pytest.mark.django_db
class TestPagesInABrowser:
    # Only what a real browser can measure belongs here. A check that works on
    # rendered HTML goes in the classes above, which cannot skip.

    @pytest.mark.parametrize("size", [PHONE, DESKTOP], ids=["phone", "desktop"])
    @pytest.mark.parametrize("name", LAYOUTS)
    def test_a_page_loads_without_an_error(
        self, chromium, live_server, page, name: str, size: dict[str, int]
    ) -> None:
        # A script that throws, or a file that is not served, leaves the markup
        # intact and the page broken.
        errors: list[str] = []
        page.on("pageerror", lambda exception: errors.append(str(exception)))
        page.on(
            "console", lambda m: errors.append(m.text) if m.type == "error" else None
        )
        page.on("requestfailed", lambda r: errors.append(f"failed: {r.url}"))
        page.on(
            "response",
            lambda r: (
                errors.append(f"{r.status}: {r.url}") if r.status >= 400 else None
            ),
        )
        page.set_viewport_size(size)

        page.goto(live_server.url + reverse(name))
        page.wait_for_load_state()

        assert errors == []

    def test_typing_a_code_redraws_the_preview(
        self, chromium, live_server, page
    ) -> None:
        page.set_viewport_size(DESKTOP)
        page.goto(live_server.url + reverse("playground"))

        page.fill("#lp-code", "hhh lpr fff")

        page.wait_for_selector('#lp-layout[data-mvpl-view="hhh lpr fff"]')
