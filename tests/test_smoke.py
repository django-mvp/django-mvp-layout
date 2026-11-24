"""The package installs and exposes what a consuming project needs from it."""

from pathlib import Path

from django.apps import apps

import mvp_layout

PACKAGE_ROOT = Path(mvp_layout.__file__).parent
COTTON_ROOT = PACKAGE_ROOT / "templates" / "cotton" / "layout"


class TestPackagedApp:
    def test_app_is_installed(self) -> None:
        assert apps.is_installed("mvp_layout")

    def test_components_are_where_cotton_looks_for_them(self) -> None:
        # The directory name is the first segment of every tag, and a component
        # Cotton cannot find renders as empty output rather than raising.
        assert COTTON_ROOT.is_dir()
