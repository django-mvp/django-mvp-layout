"""The committed stylesheet is the one scripts/build_css.py writes."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STYLESHEET = ROOT / "mvp_layout" / "static" / "mvp_layout" / "layout.css"


class TestTheStylesheet:
    def test_the_committed_stylesheet_is_up_to_date(self) -> None:
        built = subprocess.run(  # noqa: S603 - runs this repository's own script
            [sys.executable, str(ROOT / "scripts" / "build_css.py"), "--stdout"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        assert built == STYLESHEET.read_text(), (
            "Run python scripts/build_css.py and commit the result."
        )
