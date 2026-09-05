from django.urls import path
from . import views

urlpatterns = [
    path('receipt/<int:payment_id>/', views.receipt_view, name='view_receipt'),
    path('receipt/<int:payment_id>/pdf/', views.download_receipt_pdf_view, name='download_receipt_pdf'),
    path('receipt/<int:payment_id>/send-email/', views.send_receipt_email_view, name='send_receipt_email'),
    path('track/', views.track_view, name='track'),
    path('track/pdf/', views.download_history_pdf_view, name='download_history_pdf'),
]
