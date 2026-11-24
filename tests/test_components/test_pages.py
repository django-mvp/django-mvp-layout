"""Tests that the prototype's demonstration layouts are written as components."""

import re
from pathlib import Path

import pytest
from django.urls import reverse

from tests.conftest import elements_of

PAGES_DIR = Path(__file__).parents[1] / "templates" / "components"
PAGES = ["overview", "playground", "nested"]

pytestmark = pytest.mark.django_db


def package_attributes(source):
    """Return the package's data attributes a template writes by hand."""
    return set(re.findall(r"data-mvpl-[a-z-]+", source))


class TestPagesWrittenAsComponents:
    """SC-001: every layout on the three pages is written with the six components."""

    @pytest.mark.parametrize("name", [*PAGES, "base"])
    def test_a_page_calls_no_layout_tag_and_mounts_no_script(self, name):
        source = (PAGES_DIR / f"{name}.html").read_text()

        assert "layout_attrs" not in source
        assert "sidebar_attrs" not in source
        assert "MvpLayout" not in source

    @pytest.mark.parametrize("name", [*PAGES, "base"])
    def test_a_page_writes_no_data_attribute_but_the_two_content_hooks(self, name):
        source = (PAGES_DIR / f"{name}.html").read_text()

        # Both hooks sit on content the page puts in a layout: one shows an
        # element in one state of a sidebar, one closes the drawer around a
        # button. No component writes either.
        assert package_attributes(source) <= {"data-mvpl-when", "data-mvpl-close"}

    @pytest.mark.parametrize("name", PAGES)
    def test_a_page_renders(self, client, name):
        response = client.get(reverse(f"components-{name}"))

        assert response.status_code == 200

    def test_the_pages_hold_every_layout_the_prototype_shows(self, client):
        layouts = {
            name: sum(
                "data-mvpl" in attrs and "data-mvpl-side" not in attrs
                for _, attrs in elements_of(
                    client.get(reverse(f"components-{name}")).content.decode()
                )
            )
            for name in PAGES
        }

        # The shell on every page, then the playground's preview and the nested
        # page's inbox, settings dialog, project, document and filters layouts.
        assert layouts == {"overview": 1, "playground": 2, "nested": 6}


class TestIds:
    """SC-004: nothing on a page with several nested layouts repeats an id."""

    @pytest.mark.parametrize("name", PAGES)
    def test_no_id_repeats(self, client, name):
        html = client.get(reverse(f"components-{name}")).content.decode()
        ids = [attrs["id"] for _, attrs in elements_of(html) if "id" in attrs]

        assert len(ids) == len(set(ids))
