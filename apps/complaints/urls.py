from django.urls import path
from . import views

urlpatterns = [
    path('', views.complaint_list_view, name='complaint_list'),
    path('submit/', views.submit_complaint_view, name='submit_complaint'),
]
