from django.urls import path

from . import views
from . import razorpay_views

app_name = 'orders'

urlpatterns = [
    # Prescription upload and processing
    path('upload-prescription/', views.upload_prescription, name='upload_prescription'),
    path('prescription/<int:prescription_id>/medicines/', views.prescription_medicines, name='prescription_medicines'),
    path('prescription/<int:prescription_id>/bill/', views.generate_bill, name='generate_bill'),

    # Prescription verification (for pharmacists)
    path('prescription/<int:prescription_id>/verify/', views.verify_prescription, name='verify_prescription'),
    path('prescription/<int:prescription_id>/detail/', views.prescription_detail, name='prescription_detail'),
    
    # Cart functionality
    path('add-to-cart/<int:medicine_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('update-cart/<int:medicine_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove-from-cart/<int:medicine_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    
    # Order management
    path('create/', views.create_order, name='create'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('pharmacy-orders/', views.pharmacy_orders, name='pharmacy_orders'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('bill/<int:order_id>/', views.order_bill, name='order_bill'),
    path('update-status/<int:order_id>/', views.update_order_status, name='update_status'),
    
    # Advance orders
    path('advance-orders/', views.advance_orders, name='advance_orders'),
    path('advance-order/<int:order_id>/', views.advance_order_detail, name='advance_order_detail'),
    path('create-advance-order/', views.create_advance_order, name='create_advance_order'),
    path('update-advance-order-status/<int:order_id>/', views.update_advance_order_status, name='update_advance_order_status'),
    
    # Legacy routes
    path('select-medicines/', views.select_medicines, name='select_medicines'),
    
    # API endpoints
    path('api/orders-data/', views.get_orders_data, name='get_orders_data'),
    path('api/pharmacy-dashboard-data/', views.get_pharmacy_dashboard_data, name='get_pharmacy_dashboard_data'),

    # Razorpay integration endpoints
    path('create-razorpay-order/', razorpay_views.create_razorpay_order, name='create_razorpay_order'),
    path('razorpay-callback/', razorpay_views.razorpay_callback, name='razorpay_callback'),

    # API endpoints
    path('api/orders/', views.orders_api, name='orders_api'),
]
