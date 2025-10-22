# converter/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('charts/', views.charts_view, name='charts'),
]