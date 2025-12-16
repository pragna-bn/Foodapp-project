from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Main app (Home page only)
    path('', include('main.urls')),

    # Restaurants app
    path('restaurants/', include('restaurants.urls')),

    # Orders app
    path('orders/', include('orders.urls')),
]

# MEDIA settings
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)