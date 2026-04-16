from django.urls import path
from . import views

urlpatterns = [
    path('',                              views.quote_request, name='quote_request'),
    path('success/',                      views.quote_success,  name='quote_success'),
    path('invoice/<str:invoice_number>/', views.invoice_view,   name='invoice_view'),
]
