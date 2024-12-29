# utils.py
from django.utils import timezone


def get_today():
    """Return the current date in the local timezone."""
    return timezone.localdate()
