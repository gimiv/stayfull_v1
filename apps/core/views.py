"""
Core views for Stayfull PMS.
"""
from django.shortcuts import redirect


def root_redirect(request):
    """Redirect root URL to API documentation."""
    return redirect('/api/docs/')
