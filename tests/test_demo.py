"""The demo project's pages respond and are built on the layout."""

import pytest
from django.urls import reverse

PAGES = ["home", "playground", "nested", "plain"]


class TestTheDemoPages:
    @pytest.mark.parametrize("name", PAGES)
    def test_each_page_is_a_layout(self, client, name) -> None:
        response = client.get(reverse(name))
        assert response.status_code == 200
        assert "data-mvpl-view" in response.content.decode()

    def test_the_playground_draws_the_code_it_is_given(self, client) -> None:
        html = client.get(
            reverse("playground"), {"view": "hHh LpR fFf"}
        ).content.decode()
        assert 'data-mvpl-view="hHh LpR fFf"' in html

    def test_the_playground_refuses_a_wrong_code_without_failing(self, client) -> None:
        assert client.get(reverse("playground"), {"view": "nope"}).status_code == 200

    def test_the_playground_preview_is_a_fragment(self, client) -> None:
        response = client.get(reverse("playground"), headers={"X-Preview": "1"})
        assert response.status_code == 200
        assert "<html" not in response.content.decode()

    def test_the_without_cotton_page_is_the_documented_base(self, client) -> None:
        # The page extends docs/examples/base.html, so the example cannot drift.
        html = client.get(reverse("plain")).content.decode()
        assert 'id="app"' in html
        assert 'data-persist="nav"' in html
