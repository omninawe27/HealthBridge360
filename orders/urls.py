from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.create_order, name='create'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('pharmacy-orders/', views.pharmacy_orders, name='pharmacy_orders'),
    path('detail/<int:order_id>/', views.order_detail, name='detail'),
    path('upload-prescription/', views.upload_prescription, name='upload_prescription'),
    path('select-medicines/', views.select_medicines, name='select_medicines'),
    path('update-status/<int:order_id>/', views.update_order_status, name='update_status'),
    path('add-to-cart/<int:medicine_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('update-cart/<int:medicine_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove-from-cart/<int:medicine_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('api/orders-data/', views.get_orders_data, name='get_orders_data'),
]
