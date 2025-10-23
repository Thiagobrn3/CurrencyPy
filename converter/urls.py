# converter/urls.py
from django.urls import path
from .views import HomeView, ChartsView

urlpatterns = [
    # Usamos .as_view() para conectar las CBV a las rutas
    path('', HomeView.as_view(), name='home'),
    path('charts/', ChartsView.as_view(), name='charts'),
]