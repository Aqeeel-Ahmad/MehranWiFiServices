from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Custom Admin Site Branding
admin.site.site_header = "Mehran WiFi Service - Admin Portal"
admin.site.site_title = "Mehran WiFi Admin"
admin.site.index_title = "Fiber ISP Infrastructure & Subscriber Management"

from apps.accounts import views as account_views
from apps.payments import views as payment_views
from apps.core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Main Navigation Direct Routes
    path('', include('apps.core.urls')),
    path('packages/', include('apps.packages.urls')),
    path('track/', payment_views.track_view, name='track'),
    path('about/', core_views.about_view, name='about'),
    path('contact/', core_views.contact_view, name='contact'),

    # Direct User Auth & Dashboard Routes
    path('login/', account_views.login_view, name='login'),
    path('register/', account_views.register_view, name='register'),
    path('logout/', account_views.logout_view, name='logout'),
    path('dashboard/', account_views.dashboard_view, name='dashboard'),
    path('profile/', account_views.profile_view, name='profile'),

    # App Namespaces
    path('accounts/', include('apps.accounts.urls')),
    path('payments/', include('apps.payments.urls')),
    path('complaints/', include('apps.complaints.urls')),
    path('notifications/', include('apps.notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
