from django.urls import path
from . import views

urlpatterns = [
    # Contact/Quote form endpoint
    path('contact/', views.quote_request, name='quote_request'),

    # Success page
    path('success/', views.quote_success, name='quote_success'),

    # Invoice view
    path('invoice/<str:invoice_number>/', views.invoice_view, name='invoice_view'),
]
