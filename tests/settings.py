"""Django settings for testing django-mvp-layout."""

# Everything else is inherited from demo/settings.py rather than restated, so the
# suite cannot stay green against its own copy while the demo is broken.
from demo.settings import *  # noqa: F403

SECRET_KEY = "django-insecure-test-key-for-mvp_layout-tests-only"

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]

# The demo's routes, behind a urlconf of the suite's own so a test-only route
# has somewhere to go.
ROOT_URLCONF = "tests.urls"

# Templates that exist only to put something in one exact situation a test
# needs. They are not part of the demo project and are never distributed.
TEMPLATES[0]["DIRS"] = [  # noqa: F405
    *TEMPLATES[0]["DIRS"],  # noqa: F405
    BASE_DIR / "tests" / "templates",  # noqa: F405
    # A test page extends examples/base.html.
    BASE_DIR / "docs",  # noqa: F405
]

# The component test pages draw icons with a tag library in tests/templatetags.
INSTALLED_APPS = [*INSTALLED_APPS, "tests"]  # noqa: F405
