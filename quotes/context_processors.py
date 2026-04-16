"""
quotes/context_processors.py
==============================
Injects the AGENCY dict into every template automatically.
This is why {{ agency.name }} works in base.html without
the view explicitly passing it in context.
"""

from django.conf import settings


def agency_context(request):
    """Add AGENCY settings to every template context."""
    return {'agency': settings.AGENCY}
