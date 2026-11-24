"""Django settings for testing django-mvp-layout."""

# Everything else is inherited from demo/settings.py rather than restated, so the
# suite cannot stay green against its own copy while the demo is broken.
from demo.settings import *  # noqa: F403

SECRET_KEY = "django-insecure-test-key-for-mvp_layout-tests-only"

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]

ROOT_URLCONF = "tests.urls"

# Templates that exist only to put something in one exact situation a test
# needs. They are not part of the demo project and are never distributed.
TEMPLATES[0]["DIRS"] = [*TEMPLATES[0]["DIRS"], BASE_DIR / "tests" / "templates"]  # noqa: F405
