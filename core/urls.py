from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('emergency/', views.emergency_mode, name='emergency'),
    path('search/', views.search_medicines, name='search'),
    path('change-language/', views.change_language, name='change_language'),
]
