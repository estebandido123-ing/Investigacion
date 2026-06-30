from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActaViewSet

# El router crea automáticamente las rutas estándar de la API
router = DefaultRouter()
router.register(r'actas', ActaViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]