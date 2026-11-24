"""A layout written with components carries what the same layout in tags does."""

import pytest
from django.template import Context, Template
from django.urls import reverse

from tests.conftest import elements_of, with_data

pytestmark = pytest.mark.django_db

PLAIN_LAYOUT = """{% load mvp_layout %}
<div {% layout_attrs "lHh LpR lff" container=True css_class="frame" %}>
  <div class="mvpl-grid">
    <aside {% sidebar_attrs "left" collapse="icons" persist="nav" width="14rem" %}>
      <div class="mvpl-backdrop" data-mvpl-close aria-hidden="true"></div>
      <div class="mvpl-panel">x</div>
    </aside>
    <aside {% sidebar_attrs "right" behavior="docked" closed=True %}>
      <div class="mvpl-backdrop" data-mvpl-close aria-hidden="true"></div>
      <div class="mvpl-panel">y</div>
    </aside>
  </div>
</div>
"""

COMPONENT_LAYOUT = """
<c-layout view="lHh LpR lff" container class="frame">
  <c-layout.sidebar side="left" collapse="icons" persist="nav"
                    width="14rem">x</c-layout.sidebar>
  <c-layout.sidebar side="right" behavior="docked" closed>y</c-layout.sidebar>
</c-layout>
"""


def hooks_of(html):
    """Return the toggles' ``(side, when)`` pairs the script reads, in order."""
    return [
        (attrs["data-mvpl-toggle"], attrs.get("data-mvpl-when"))
        for tag, attrs in elements_of(html)
        if tag == "button" and "data-mvpl-toggle" in attrs
    ]


class TestParity:
    """SC-002: components and tags render the same attributes."""

    def test_a_layout_with_two_sidebars_matches_the_same_layout_in_tags(self, render):
        plain = Template(PLAIN_LAYOUT).render(Context())

        assert with_data(render(COMPONENT_LAYOUT)) == with_data(plain)

    def test_toggles_carry_the_hooks_the_plain_templates_toggles_carry(
        self, client, render
    ):
        plain = hooks_of(client.get(reverse("layouts-toggles")).content.decode())
        components = hooks_of(
            render(
                '<c-layout.toggle side="left" />'
                '<c-layout.toggle side="left" when="closed" />'
                '<c-layout.toggle side="left" when="open" />'
                '<c-layout.toggle side="right" />'
            )
        )

        assert sorted(components, key=str) == sorted(plain, key=str)
