"""
CJ Web Studio — URL Configuration
===================================
All URLs for the project are registered here.
The admin panel lives at /admin/
Everything else is handled by the quotes app.
"""

from django.contrib import admin
from django.urls import path, include

# Customise the admin site header to match CJ Web Studio branding
admin.site.site_header  = 'CJ Web Studio — Admin'
admin.site.site_title   = 'CJ Web Studio'
admin.site.index_title  = 'Client Pipeline Dashboard'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('quotes.urls')),  # All quote-related pages
]
