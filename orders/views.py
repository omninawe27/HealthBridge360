from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum
from .models import Order, OrderItem
from .forms import OrderForm, PrescriptionUploadForm
from medicines.models import Medicine
from pharmacy.models import Pharmacy

@login_required
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            messages.success(request, 'Order created successfully!')
            return redirect('orders:detail', order_id=order.id)
    else:
        form = OrderForm()
    
    return render(request, 'orders/create.html', {'form': form})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Check if user owns the order or is the pharmacy owner
    if order.user != request.user and (not hasattr(request.user, 'pharmacy') or order.pharmacy != request.user.pharmacy):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    return render(request, 'orders/detail.html', {'order': order})

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})

@login_required
def pharmacy_orders(request):
    """View orders for pharmacy owners"""
    if not hasattr(request.user, 'pharmacy'):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    pharmacy = request.user.pharmacy
    orders = Order.objects.filter(pharmacy=pharmacy).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        orders = orders.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(id__icontains=search_query) |
            Q(items__medicine__name__icontains=search_query)
        ).distinct()
    
    # Date range filter
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)
    
    context = {
        'orders': orders,
        'pharmacy': pharmacy,
        'pending_count': orders.filter(status='pending').count(),
        'confirmed_count': orders.filter(status='confirmed').count(),
        'ready_count': orders.filter(status='ready').count(),
        'delivered_count': orders.filter(status='delivered').count(),
        'total_orders': orders.count(),
        'total_revenue': orders.filter(status='delivered').aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
    }
    return render(request, 'orders/pharmacy_orders.html', context)

@login_required
def upload_prescription(request):
    if request.method == 'POST':
        form = PrescriptionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Process prescription image (OCR would go here)
            prescription_image = form.cleaned_data['prescription_image']
            
            # For now, redirect to manual medicine selection
            # In a real app, you'd use OCR to extract medicine names
            messages.success(request, 'Prescription uploaded successfully! Please select medicines and quantities.')
            return redirect('orders:select_medicines')
    else:
        form = PrescriptionUploadForm()
    
    return render(request, 'orders/upload_prescription.html', {'form': form})

@login_required
def select_medicines(request):
    medicines = Medicine.objects.filter(quantity__gt=0).order_by('name')
    return render(request, 'orders/select_medicines.html', {'medicines': medicines})

@login_required
def update_order_status(request, order_id):
    if not hasattr(request.user, 'pharmacy'):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    order = get_object_or_404(Order, id=order_id, pharmacy=request.user.pharmacy)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            old_status = order.status
            order.status = new_status
            order.save()
            
            # Send notification to customer if status changed
            if old_status != new_status:
                # In a real app, you'd send email/SMS here
                pass
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Order status updated to {order.get_status_display()}',
                    'new_status': new_status,
                    'status_display': order.get_status_display()
                })
            else:
                messages.success(request, f'Order status updated to {order.get_status_display()}')
    
    return redirect('orders:detail', order_id=order.id)

@login_required
def get_orders_data(request):
    """AJAX endpoint to get orders data for real-time updates"""
    if not hasattr(request.user, 'pharmacy'):
        return JsonResponse({'success': False, 'message': 'Access denied'})
    
    pharmacy = request.user.pharmacy
    orders = Order.objects.filter(pharmacy=pharmacy).order_by('-created_at')
    
    # Get recent orders for dashboard
    recent_orders = orders[:10]
    
    orders_data = []
    for order in recent_orders:
        orders_data.append({
            'id': order.id,
            'customer_name': f"{order.user.first_name} {order.user.last_name}",
            'status': order.status,
            'status_display': order.get_status_display(),
            'total_amount': str(order.total_amount),
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
            'items_count': order.items.count(),
        })
    
    # Get statistics
    stats = {
        'pending_count': orders.filter(status='pending').count(),
        'confirmed_count': orders.filter(status='confirmed').count(),
        'ready_count': orders.filter(status='ready').count(),
        'delivered_count': orders.filter(status='delivered').count(),
        'total_orders': orders.count(),
        'total_revenue': str(orders.filter(status='delivered').aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
    }
    
    return JsonResponse({
        'success': True,
        'orders': orders_data,
        'stats': stats
    })

@login_required
def add_to_cart(request, medicine_id):
    """AJAX endpoint to add medicine to cart"""
    if request.method == 'POST':
        try:
            medicine = get_object_or_404(Medicine, id=medicine_id, quantity__gt=0)
            quantity = int(request.POST.get('quantity', 1))
            
            if quantity > medicine.quantity:
                return JsonResponse({
                    'success': False,
                    'message': f'Only {medicine.quantity} units available'
                })
            
            # Get or create cart session
            cart = request.session.get('cart', {})
            medicine_key = str(medicine_id)
            
            if medicine_key in cart:
                cart[medicine_key]['quantity'] += quantity
            else:
                cart[medicine_key] = {
                    'medicine_id': medicine_id,
                    'name': medicine.name,
                    'brand': medicine.brand,
                    'price': str(medicine.price),
                    'quantity': quantity,
                    'pharmacy_id': medicine.pharmacy.id,
                    'pharmacy_name': medicine.pharmacy.name
                }
            
            request.session['cart'] = cart
            request.session.modified = True
            
            # Calculate total items in cart
            total_items = sum(item['quantity'] for item in cart.values())
            
            return JsonResponse({
                'success': True,
                'message': 'Medicine added to cart',
                'cart_count': total_items
            })
            
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'Invalid quantity'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def view_cart(request):
    """View shopping cart"""
    cart = request.session.get('cart', {})
    cart_items = []
    total_amount = 0
    
    for item_data in cart.values():
        try:
            medicine = Medicine.objects.get(id=item_data['medicine_id'])
            if medicine.quantity >= item_data['quantity']:
                item_total = medicine.price * item_data['quantity']
                cart_items.append({
                    'medicine': medicine,
                    'quantity': item_data['quantity'],
                    'total': item_total
                })
                total_amount += item_total
            else:
                # Remove from cart if not enough stock
                del cart[item_data['medicine_id']]
        except Medicine.DoesNotExist:
            # Remove from cart if medicine doesn't exist
            del cart[item_data['medicine_id']]
    
    request.session['cart'] = cart
    request.session.modified = True
    
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'cart_count': len(cart_items)
    }
    return render(request, 'orders/cart.html', context)

@login_required
def update_cart_item(request, medicine_id):
    """Update cart item quantity"""
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        medicine_key = str(medicine_id)
        
        if medicine_key in cart:
            quantity = int(request.POST.get('quantity', 0))
            
            if quantity <= 0:
                del cart[medicine_key]
            else:
                # Check if quantity is available
                try:
                    medicine = Medicine.objects.get(id=medicine_id)
                    if quantity <= medicine.quantity:
                        cart[medicine_key]['quantity'] = quantity
                    else:
                        return JsonResponse({
                            'success': False,
                            'message': f'Only {medicine.quantity} units available'
                        })
                except Medicine.DoesNotExist:
                    del cart[medicine_key]
            
            request.session['cart'] = cart
            request.session.modified = True
            
            total_items = sum(item['quantity'] for item in cart.values())
            
            return JsonResponse({
                'success': True,
                'cart_count': total_items
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def remove_from_cart(request, medicine_id):
    """Remove item from cart"""
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        medicine_key = str(medicine_id)
        
        if medicine_key in cart:
            del cart[medicine_key]
            request.session['cart'] = cart
            request.session.modified = True
            
            total_items = sum(item['quantity'] for item in cart.values())
            
            return JsonResponse({
                'success': True,
                'cart_count': total_items
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def checkout(request):
    """Checkout process"""
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.warning(request, 'Your cart is empty')
        return redirect('orders:view_cart')
    
    if request.method == 'POST':
        # Get pharmacy from first item
        first_item = next(iter(cart.values()))
        pharmacy = get_object_or_404(Pharmacy, id=first_item['pharmacy_id'])
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            pharmacy=pharmacy,
            status='pending',
            notes=request.POST.get('notes', '')
        )
        
        # Create order items
        total_amount = 0
        for item_data in cart.values():
            medicine = Medicine.objects.get(id=item_data['medicine_id'])
            quantity = item_data['quantity']
            price = medicine.price
            
            OrderItem.objects.create(
                order=order,
                medicine=medicine,
                quantity=quantity,
                price=price
            )
            
            # Update medicine stock
            medicine.quantity -= quantity
            medicine.save()
            
            total_amount += price * quantity
        
        # Update order total
        order.total_amount = total_amount
        order.save()
        
        # Clear cart
        request.session['cart'] = {}
        request.session.modified = True
        
        messages.success(request, 'Order placed successfully!')
        return redirect('orders:detail', order_id=order.id)
    
    # Calculate totals
    cart_items = []
    total_amount = 0
    
    for item_data in cart.values():
        medicine = Medicine.objects.get(id=item_data['medicine_id'])
        item_total = medicine.price * item_data['quantity']
        cart_items.append({
            'medicine': medicine,
            'quantity': item_data['quantity'],
            'total': item_total
        })
        total_amount += item_total
    
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount
    }
    return render(request, 'orders/checkout.html', context)
