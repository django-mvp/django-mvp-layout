"""Settings for the demo project, a demonstration target that is never deployed.

The demo runs on Django, django-cotton and this package alone, so it shows
what a project with none of django-mvp gets. Its stylesheet is Tailwind and
daisyUI, built by ``npm run build:css``.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-demo-project-only"

DEBUG = True

# The development server is reached over the network by hostname, not only at
# localhost. DEBUG auto-allows localhost and nothing else.
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "demo",
    "mvp_layout",
    "django.contrib.staticfiles",
    "django_cotton",
    # Reloads the browser on a change to a template, a stylesheet or Python. Its
    # middleware removes itself from the chain unless DEBUG is on.
    "django_browser_reload",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Last, because it rewrites the response body to insert its script tag.
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = "demo.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # The base template the docs give for a project without django-cotton,
        # which the demo's "Without Cotton" page extends.
        "DIRS": [BASE_DIR / "docs" / "examples"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                # The sidebars read their remembered state from the request.
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "demo.wsgi.application"

# Nothing is stored. Django's test runner still wants a database to set up.
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

STATIC_URL = "/static/"

USE_TZ = True
USE_I18N = True
LANGUAGE_CODE = "en-us"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
