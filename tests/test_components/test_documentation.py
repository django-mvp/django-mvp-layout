"""Tests that each component's attributes are declared and documented."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
COMPONENTS = ROOT / "mvp_layout" / "templates" / "cotton" / "layout"
PAGE = ROOT / "docs" / "developer" / "cotton.md"

# Each component's section of the components page.
SECTIONS = {
    "index": "`<c-layout>`",
    "header": "`<c-layout.header>`, `<c-layout.page>`, `<c-layout.footer>`",
    "page": "`<c-layout.header>`, `<c-layout.page>`, `<c-layout.footer>`",
    "footer": "`<c-layout.header>`, `<c-layout.page>`, `<c-layout.footer>`",
    "body": "`<c-layout.body>`",
    "sidebar": "`<c-layout.sidebar>`",
    "toggle": "`<c-layout.toggle>`",
}


def declared(name):
    """Return the attribute names a component's ``<c-vars>`` declares."""
    source = (COMPONENTS / f"{name}.html").read_text()
    tag = re.search(r"<c-vars\s+(.*?)/>", source, re.S).group(1)
    return set(re.findall(r"([\w-]+)=", tag))


def described(name):
    """Return the attribute names a component's ``@prop`` comments describe."""
    source = (COMPONENTS / f"{name}.html").read_text()
    return set(re.findall(r"@prop ([\w-]+):", source))


def documented(heading):
    """Return the attribute names in the table under a heading of the page."""
    page = PAGE.read_text()
    section = page.split(f"## {heading}\n", 1)[1].split("\n## ", 1)[0]
    return set(re.findall(r"^\| `([\w-]+)` \|", section, re.M))


class TestComponentAttributes:
    """SC-003: every attribute a component accepts is documented, and no other."""

    @pytest.mark.parametrize("name", SECTIONS)
    def test_the_prop_comments_describe_every_declared_attribute(self, name):
        assert described(name) == declared(name)

    @pytest.mark.parametrize("name", SECTIONS)
    def test_the_page_documents_every_declared_attribute(self, name):
        shared = documented(SECTIONS[name])

        assert declared(name) <= shared

    @pytest.mark.parametrize("name", SECTIONS)
    def test_the_page_documents_only_attributes_a_component_declares(self, name):
        group = [n for n, heading in SECTIONS.items() if heading == SECTIONS[name]]
        every = set().union(*(declared(n) for n in group))

        assert documented(SECTIONS[name]) == every
