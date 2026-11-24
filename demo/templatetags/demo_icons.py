"""Icons for the demo pages, drawn inline so the demo needs nothing from a CDN."""

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

# Outline shapes on a 24-unit grid, after the Lucide icon set (ISC licence).
PATHS = {
    "house": (
        '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/>'
        '<path d="M10 21v-6h4v6"/>'
    ),
    "inbox": (
        '<path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.5 5h13L22 12v7H2v-7z"/>'
    ),
    "file-text": (
        '<path d="M14 2H6v20h12V6z"/><path d="M14 2v4h4"/>'
        '<path d="M8 13h8M8 17h8M8 9h2"/>'
    ),
    "chat": (
        '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>'
    ),
    "star": (
        '<path d="m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 '
        '21l1.2-6.8-5-4.9 6.9-1z"/>'
    ),
    "gear": (
        '<circle cx="12" cy="12" r="3"/>'
        '<path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 '
        "2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 "
        "0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 "
        "1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 "
        "0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 "
        "2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 "
        "0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 "
        "2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 "
        '4h-.1a1.7 1.7 0 0 0-1.5 1z"/>'
    ),
    "search": '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
    "send": '<path d="M22 2 11 13"/><path d="M22 2 15 22l-4-9-9-4z"/>',
    "file-earmark": '<path d="M14 2H6v20h12V6z"/><path d="M14 2v4h4"/>',
    "archive": (
        '<rect x="2" y="3" width="20" height="5" rx="1"/>'
        '<path d="M4 8v13h16V8M10 12h4"/>'
    ),
    "trash": '<path d="M3 6h18M8 6V4h8v2M5 6l1 15h12l1-15"/>',
    "person": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    "bell": (
        '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/>'
        '<path d="M10.3 21a1.9 1.9 0 0 0 3.4 0"/>'
    ),
    "shield-lock": (
        '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>'
        '<rect x="9.5" y="11" width="5" height="4"/>'
        '<path d="M10.5 11V9.5a1.5 1.5 0 0 1 3 0V11"/>'
    ),
    "palette": (
        '<circle cx="12" cy="12" r="10"/><circle cx="8" cy="10" r="1"/>'
        '<circle cx="12" cy="7" r="1"/><circle cx="16" cy="10" r="1"/>'
    ),
    "key": (
        '<circle cx="7.5" cy="15.5" r="4.5"/><path d="m10.7 12.3 9.8-9.8M17 6l3 3"/>'
    ),
    "folder": (
        '<path d="M3 6a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v10a2 2 0 0 1-2 '
        '2H5a2 2 0 0 1-2-2z"/>'
    ),
    "close": '<path d="M18 6 6 18M6 6l12 12"/>',
    "funnel": '<path d="M22 3H2l8 9.5V19l4 2v-8.5z"/>',
    "copy": ('<rect x="8" y="8" width="13" height="13" rx="2"/><path d="M4 16V4h12"/>'),
    "layout": (
        '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 9v12"/>'
    ),
    "layers": (
        '<path d="m12 2 10 5-10 5L2 7z"/><path d="m2 12 10 5 10-5M2 17l10 5 10-5"/>'
    ),
    "code": '<path d="m16 18 6-6-6-6M8 6l-6 6 6 6"/>',
    "sidebar-right": (
        '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M15 4v16"/>'
    ),
}


@register.simple_tag
def icon(name, css_class=""):
    """Draw an inline SVG icon, hidden from assistive technology.

    Args:
        name: A key of ``PATHS``. An unknown name draws a dot.
        css_class: Extra classes for the ``<svg>`` element.

    Returns:
        The inline ``<svg>`` markup.
    """
    shape = PATHS.get(name, '<circle cx="12" cy="12" r="2"/>')
    return format_html(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        'width="1.25em" height="1.25em" '
        'fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true" class="shrink-0 {}">{}</svg>',
        css_class,
        mark_safe(shape),  # noqa: S308 - constant markup from this module
    )
