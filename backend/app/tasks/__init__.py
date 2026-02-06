"""Tasks package initializer."""

from .celery_app import celery_app

# Do not import task modules here — Celery will import them via the
# `include` list in `celery_app` to avoid importing application models
# at package import time (which may not be available during worker startup).
