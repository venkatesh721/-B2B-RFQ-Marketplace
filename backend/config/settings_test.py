"""Local test settings: use SQLite so tests do not need MySQL credentials."""

import os

os.environ.setdefault("DJANGO_SECRET_KEY", "test-only-secret-key-with-more-than-fifty-characters-123456789")

from .settings import *  # noqa: F403


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test.sqlite3",  # noqa: F405
    }
}

# Fast hashes are safe here because this module is only for automated tests.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Django's test client makes HTTP requests; production settings enforce HTTPS.
SECURE_SSL_REDIRECT = False
