from django.urls import path
from . import views

urlpatterns = [
    path('', views.package_list_view, name='package_list'),
    path('order/', views.order_package_wizard_view, name='order_package'),
    path('api/calculate-expiry/', views.api_calculate_expiry, name='api_calculate_expiry'),
    path('api/calculate-custom-price/', views.api_calculate_custom_price, name='api_calculate_custom_price'),
]
