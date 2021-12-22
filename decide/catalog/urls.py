from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('admin/', admin.site.urls),
    path('doc/', schema_view),
    path('gateway/', include('gateway.urls')),
]