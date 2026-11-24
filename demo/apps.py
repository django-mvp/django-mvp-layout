"""App configuration for the demo project."""

from django.apps import AppConfig


class DemoConfig(AppConfig):
    """The demo project's pages, templates and stylesheet."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "demo"
    verbose_name = "Demo"
