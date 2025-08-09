from django.urls import path
from . import views

app_name = 'medicines'

urlpatterns = [
    path('add/', views.add_medicine, name='add'),
    path('edit/<int:medicine_id>/', views.edit_medicine, name='edit'),
    path('delete/<int:medicine_id>/', views.delete_medicine, name='delete'),
    path('alternatives/', views.search_alternatives, name='alternatives'),
    path('<int:medicine_id>/alternatives/', views.get_alternatives, name='get_alternatives'),
    path('inventory/', views.inventory, name='inventory'),
    path('<int:medicine_id>/update-stock/', views.update_stock, name='update_stock'),
    path('<int:medicine_id>/details/', views.medicine_details, name='details'),
    path('bulk-update-stock/', views.bulk_update_stock, name='bulk_update_stock'),
    path('<int:medicine_id>/delete-ajax/', views.delete_medicine_ajax, name='delete_ajax'),
]
