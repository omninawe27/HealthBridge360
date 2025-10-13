from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns, set_language

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/setlang/', set_language, name='set_language'),
    path('', include('core.urls')),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('pharmacy/', include('pharmacy.urls')),
    path('medicines/', include('medicines.urls')),
    path('orders/', include('orders.urls')),
    path('reminders/', include('reminders.urls')),
]

# Wrap the URL patterns with i18n_patterns for language switching
urlpatterns = i18n_patterns(*urlpatterns)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
