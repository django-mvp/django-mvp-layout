"""The suite's urlconf: the demo project's routes plus the test pages."""

from django.urls import path

from demo.urls import urlpatterns as demo_urlpatterns
from tests.views import LayoutPage

# Each page is a template under tests/templates/layouts/ and is routed as
# layouts-<name>. Most extend the documented base template.
PAGES = (
    "default",
    "contained",
    "nested",
    "narrow-box",
    "empty-aside",
    "outside-toggle",
    "rtl",
    "toggles",
    "sidebars",
    "behaviors",
    "focus",
    "heavy",
    "host-rules",
    "host-colours",
    # Not the base template: its layout code is read from the URL.
    "code",
)

urlpatterns = [
    *demo_urlpatterns,
    *(
        path(
            f"layouts/{name}/",
            LayoutPage.as_view(template_name=f"layouts/{name}.html"),
            name=f"layouts-{name}",
        )
        for name in PAGES
    ),
]
