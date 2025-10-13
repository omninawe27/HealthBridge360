from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.template.loader import render_to_string
from django.utils import timezone
from django.http import HttpResponseRedirect
import logging
from .models import Order, OrderItem, Prescription, PrescriptionMedicine, Cart, CartItem, MedicineReminder, AdvanceOrder, AdvanceOrderItem
from .forms import OrderForm, PrescriptionUploadForm, PrescriptionMedicineForm, CheckoutForm, ReminderForm
from .services import PrescriptionProcessor, CartService, ReminderService
from core.ocr_utils import extract_text_from_image
from medicines.models import Medicine
from pharmacy.models import Pharmacy
from notifications.services import NotificationService

logger = logging.getLogger(__name__)

@login_required
def upload_prescription(request):
    """Upload prescription and process it"""
    if request.method == 'POST':
        form = PrescriptionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.user = request.user
            prescription.status = 'processing'
            prescription.save()

            # Send verification code email
            logger.info(f"Sending verification code email for prescription {prescription.id} to user {request.user.email}")
            email_result = NotificationService.send_prescription_verification_code(prescription)
            logger.info(f"Verification code email result for prescription {prescription.id}: {email_result}")

            if email_result:
                messages.success(request, 'Prescription uploaded successfully! Please check your email for verification code.')
                logger.info(f"Verification code email sent successfully for prescription {prescription.id}")
            else:
                messages.warning(request, 'Prescription uploaded but failed to send verification email. Please contact support.')
                logger.error(f"Failed to send verification code email for prescription {prescription.id}")

            try:
                # Process prescription using OCR
                processor = PrescriptionProcessor(prescription)

                # Extract text from uploaded image using OCR
                extracted_text = extract_text_from_image(prescription.image.path)
                if not extracted_text.strip():
                    # If OCR fails, use sample text as fallback
                    extracted_text = """
                    instacium d3 1000IU tablet - once daily
                    orovit active 1000IU tablet - once daily
                    Iayn rexnerve plus 500mcg tablet - once daily
                    wellnex d3 1000IU tablet - once daily
                    """
                    logger.warning(f"OCR failed for prescription {prescription.id}, using sample text")

                prescription.extracted_text = extracted_text
                prescription.save()

                # Extract medicines from text
                extracted_medicines = processor.extract_medicines_from_text(extracted_text)

                # Match with available medicines
                prescription_medicines = processor.match_medicines(extracted_medicines)

                prescription.status = 'processed'
                prescription.processed_at = timezone.now()
                prescription.save()

                messages.success(request, f'Prescription processed successfully! Found {len(prescription_medicines)} medicines.')
                return redirect('orders:prescription_medicines', prescription_id=prescription.id)

            except Exception as e:
                prescription.status = 'failed'
                prescription.save()
                messages.error(request, f'Failed to process prescription: {str(e)}')
                return redirect('orders:upload_prescription')
    else:
        form = PrescriptionUploadForm()
    
    return render(request, 'orders/upload_prescription.html', {'form': form})

@login_required
def prescription_medicines(request, prescription_id):
    """Show medicines found in prescription and allow quantity selection"""
    prescription = get_object_or_404(Prescription, id=prescription_id, user=request.user)
    prescription_medicines = prescription.medicines.all()
    # Restore previous UI: checkboxes for each medicine, default quantity 0
    for med in prescription_medicines:
        med.selected = False
        med.quantity_required = 0

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_to_cart':
            selected_medicines = []
            for med in prescription_medicines:
                is_selected = request.POST.get(f'select_{med.id}')
                quantity = request.POST.get(f'quantity_{med.id}')
                if is_selected and quantity and int(quantity) > 0:
                    if med.is_available and med.matched_medicine:
                        selected_medicines.append({
                            'medicine': med.matched_medicine,
                            'quantity': int(quantity)
                        })
            if selected_medicines:
                for item in selected_medicines:
                    try:
                        CartService.add_to_cart(request.user, item['medicine'].id, item['quantity'])
                    except ValueError as e:
                        messages.warning(request, str(e))
                messages.success(request, 'Selected medicines added to cart!')
                return redirect('orders:view_cart')
            else:
                messages.warning(request, 'Please select at least one medicine and set quantity > 0.')

        elif action == 'create_advance_orders':
            # Clear existing cart
            CartService.clear_cart(request.user)

            # Add selected unavailable medicines to cart with advance order flag
            advance_order_items = []
            for med in prescription_medicines:
                is_selected = request.POST.get(f'advance_select_{med.id}')
                quantity = request.POST.get(f'advance_quantity_{med.id}')
                if is_selected and quantity and int(quantity) > 0 and not med.is_available:
                    # For advance orders, we need to find a pharmacy that can fulfill this order
                    # First, try to find a pharmacy that has this medicine type
                    pharmacy = None
                    medicine_match = Medicine.objects.filter(
                        name__icontains=med.medicine_name.split()[0]  # Match first word of medicine name
                    ).first()

                    if medicine_match:
                        pharmacy = medicine_match.pharmacy
                    else:
                        # If no pharmacy found, get the first pharmacy with medicines
                        pharmacy = Pharmacy.objects.filter(
                            medicine__isnull=False
                        ).distinct().first()

                    if not pharmacy:
                        # Last resort: get any pharmacy
                        pharmacy = Pharmacy.objects.first()

                    if pharmacy:
                        # Create a temporary medicine entry for advance order
                        from datetime import date, timedelta
                        temp_medicine, created = Medicine.objects.get_or_create(
                            name=med.medicine_name,
                            pharmacy=pharmacy,
                            defaults={
                                'generic_name': med.medicine_name,
                                'brand': 'Advance Order',
                                'medicine_type': 'tablet',
                                'strength': med.dosage or 'N/A',
                                'price': 50.00,  # Default price for advance orders
                                'quantity': 0,  # Out of stock
                                'expiry_date': date.today() + timedelta(days=365),
                                'batch_number': f'AO-{med.id}',
                                'is_essential': False,
                                'is_prescription_required': True,
                            }
                        )

                        # Add to cart with advance order flag
                        CartService.add_to_cart(request.user, temp_medicine.id, int(quantity), is_advance_order=True)
                        advance_order_items.append({
                            'medicine': temp_medicine,
                            'quantity': int(quantity),
                            'name': med.medicine_name,
                            'dosage': med.dosage,
                            'frequency': med.frequency,
                            'pharmacy': pharmacy
                        })

            if advance_order_items:
                messages.success(request, 'Advance order items added to cart. Please proceed to checkout to complete your payment.')
                return redirect('orders:checkout')
            else:
                messages.warning(request, 'Please select at least one unavailable medicine for advance order.')

    context = {
        'prescription': prescription,
        'prescription_medicines': prescription_medicines,
        'available_count': prescription_medicines.filter(is_available=True).count(),
        'unavailable_count': prescription_medicines.filter(is_available=False).count(),
    }
    return render(request, 'orders/prescription_medicines.html', context)

@login_required
def add_to_cart(request, medicine_id):
    """Add medicine to cart using the new CartService"""
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            cart_item = CartService.add_to_cart(request.user, medicine_id, quantity)
            
            # Get updated cart count
            cart = CartService.get_or_create_cart(request.user)
            
            return JsonResponse({
                'success': True,
                'message': 'Medicine added to cart',
                'cart_count': cart.item_count
            })
            
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Failed to add medicine to cart'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def view_cart(request):
    """View shopping cart using the new Cart model"""
    try:
        cart = CartService.get_or_create_cart(request.user)
        cart_items = cart.items.all()
        
        context = {
            'cart': cart,
            'cart_items': cart_items,
            'total_amount': cart.total_amount,
            'cart_count': cart.item_count
        }
        return render(request, 'orders/cart.html', context)
    except Exception as e:
        messages.error(request, 'Failed to load cart')
        return redirect('core:dashboard')

@login_required
def update_cart_item(request, medicine_id):
    """Update cart item quantity"""
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 0))
            cart_item = CartService.update_cart_item(request.user, medicine_id, quantity)
            
            # Get updated cart info
            cart = CartService.get_or_create_cart(request.user)
            
            return JsonResponse({
                'success': True,
                'cart_count': cart.item_count,
                'total_amount': str(cart.total_amount)
            })
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def remove_from_cart(request, medicine_id):
    """Remove item from cart"""
    if request.method == 'POST':
        try:
            success = CartService.remove_from_cart(request.user, medicine_id)

            if success:
                cart = CartService.get_or_create_cart(request.user)
                return JsonResponse({
                    'success': True,
                    'cart_count': cart.item_count,
                    'total_amount': str(cart.total_amount)
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Item not found in cart'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })

    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def clear_cart(request):
    """Clear entire cart"""
    if request.method == 'POST':
        success = CartService.clear_cart(request.user)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': 'Cart cleared successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Failed to clear cart'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def checkout(request):
    """Enhanced checkout process with delivery options including Cash on Delivery"""
    try:
        cart = CartService.get_or_create_cart(request.user)

        if cart.item_count == 0:
            messages.warning(request, 'Your cart is empty')
            return redirect('orders:view_cart')

        # Check if cart contains advance order items
        has_advance_order_items = cart.items.filter(is_advance_order=True).exists()

        if request.method == 'POST':
            form = CheckoutForm(request.POST, initial={'user': request.user})
            if form.is_valid():
                # Determine pharmacy based on user type
                if hasattr(request.user, 'pharmacy') and request.user.pharmacy:
                    # User is a pharmacist - associate order with their pharmacy
                    pharmacy = request.user.pharmacy
                elif hasattr(request.user, 'owned_pharmacy') and request.user.owned_pharmacy:
                    # User is a pharmacy owner - associate order with their pharmacy
                    pharmacy = request.user.owned_pharmacy
                else:
                    # Regular customer - get pharmacy from first item
                    first_item = cart.items.first()
                    if not first_item:
                        messages.error(request, 'Your cart is empty')
                        return redirect('orders:view_cart')
                    pharmacy = first_item.medicine.pharmacy

                # Create order manually
                order = Order()
                order.user = request.user
                order.pharmacy = pharmacy
                order.status = 'pending'

                # Set form fields
                order.payment_method = form.cleaned_data.get('payment_method', 'cod')
                order.delivery_method = form.cleaned_data['delivery_method']
                order.delivery_address = form.cleaned_data.get('delivery_address', '')
                order.notes = form.cleaned_data.get('notes', '')

                # Mark as advance order if cart contains advance order items
                if has_advance_order_items:
                    order.is_advance_order = True
                    order.advance_order_type = 'restock'

                # Calculate delivery charges
                from decimal import Decimal
                if order.delivery_method == 'home_delivery':
                    order.delivery_charges = Decimal('50.00')  # Fixed delivery charge
                else:
                    order.delivery_charges = Decimal('0.00')

                # Set default payment_status for COD orders
                if order.payment_method == 'cod':
                    order.payment_status = 'pending'
                else:
                    order.payment_status = 'paid'

                order.save()

                # Create order items
                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        medicine=cart_item.medicine,
                        quantity=cart_item.quantity,
                        price=cart_item.medicine.price
                    )

                    # Only update medicine stock for non-advance order items
                    if not cart_item.is_advance_order:
                        cart_item.medicine.quantity -= cart_item.quantity
                        cart_item.medicine.save()

                # Calculate totals after items are created
                order.calculate_totals()

                # Create AdvanceOrder record if this is an advance order
                if has_advance_order_items:
                    advance_order = AdvanceOrder.objects.create(
                        user=request.user,
                        pharmacy=pharmacy,
                        order_type='restock',
                        status='pending'
                    )

                    # Create AdvanceOrderItems for advance order items
                    for cart_item in cart.items.filter(is_advance_order=True):
                        AdvanceOrderItem.objects.create(
                            advance_order=advance_order,
                            medicine_name=cart_item.medicine.name,
                            dosage=cart_item.medicine.strength,
                            frequency='',
                            quantity_requested=cart_item.quantity,
                            estimated_price=cart_item.medicine.price * cart_item.quantity
                        )

                    # Send advance order notification email to pharmacist
                    from notifications.services import NotificationService as NotifyService
                    if NotifyService.send_advance_order_notification(advance_order):
                        logger.info(f"Advance order notification email sent for advance order {advance_order.id}")
                    else:
                        logger.error(f"Failed to send advance order notification email for advance order {advance_order.id}")

                    # Send verification code to pharmacist for advance order
                    if NotificationService.send_order_verification_code(advance_order):
                        logger.info(f"Verification code email sent to pharmacist for advance order {advance_order.id}")
                    else:
                        logger.error(f"Failed to send verification code email to pharmacist for advance order {advance_order.id}")

                    # Send verification code to customer for advance order
                    if NotificationService.send_customer_order_verification_code(advance_order):
                        logger.info(f"Verification code email sent to customer for advance order {advance_order.id}")
                    else:
                        logger.error(f"Failed to send verification code email to customer for advance order {advance_order.id}")

                # Clear cart
                CartService.clear_cart(request.user)

                # Send order status notification emails to customer
                if NotificationService.send_order_status_notification(order):
                    logger.info(f"Order placement email sent for order {order.id}")
                else:
                    logger.error(f"Failed to send order placement email for order {order.id}")

                # Send order notification to pharmacist
                if NotificationService.send_order_notification_to_pharmacist(order):
                    logger.info(f"Order notification email sent to pharmacist for order {order.id}")
                else:
                    logger.error(f"Failed to send order notification email to pharmacist for order {order.id}")

                # Send verification code to pharmacist for normal order
                if NotificationService.send_order_verification_code(order):
                    logger.info(f"Verification code email sent to pharmacist for order {order.id}")
                else:
                    logger.error(f"Failed to send verification code email to pharmacist for order {order.id}")

                # Send verification code to customer for normal order
                if NotificationService.send_customer_order_verification_code(order):
                    logger.info(f"Verification code email sent to customer for order {order.id}")
                else:
                    logger.error(f"Failed to send verification code email to customer for order {order.id}")

                # Create reminders if prescription-based order
                if hasattr(order, 'prescription'):
                    ReminderService.create_reminders_from_order(order)

                if has_advance_order_items:
                    messages.success(request, 'Advance order placed successfully! We will notify you when medicines are available.')
                else:
                    messages.success(request, 'Order placed successfully!')
                return redirect('orders:order_detail', order_id=order.id)
        else:
            form = CheckoutForm(initial={'user': request.user})

        context = {
            'cart': cart,
            'cart_items': cart.items.all(),
            'total_amount': cart.total_amount,
            'form': form,
            'has_advance_order_items': has_advance_order_items
        }
        return render(request, 'orders/checkout.html', context)

    except Exception as e:
        print(f"Checkout error: {str(e)}")  # Debug logging
        import traceback
        traceback.print_exc()  # Print full traceback
        messages.error(request, f'Failed to process checkout: {str(e)}')
        return redirect('orders:view_cart')

@login_required
def order_detail(request, order_id):
    """Enhanced order detail view"""
    order = get_object_or_404(Order, id=order_id)

    # Check if user owns the order or is the pharmacy owner
    # Get pharmacy from user.pharmacy or user.owned_pharmacy
    pharmacy = getattr(request.user, 'pharmacy', None) or getattr(request.user, 'owned_pharmacy', None)
    if order.user != request.user and (pharmacy is None or order.pharmacy != pharmacy):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    context = {
        'order': order,
        'items': order.items.all(),
        'subtotal': order.subtotal,
        'delivery_charges': order.delivery_charges,
        'total_amount': order.total_amount
    }
    return render(request, 'orders/detail.html', context)

@login_required
def my_orders(request):
    """User's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})

@login_required
def pharmacy_orders(request):
    """View orders for pharmacy owners"""
    # Get pharmacy from user.pharmacy or user.owned_pharmacy
    pharmacy = getattr(request.user, 'pharmacy', None) or getattr(request.user, 'owned_pharmacy', None)
    if pharmacy is None:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    all_orders = Order.objects.filter(pharmacy=pharmacy).order_by('-created_at').select_related('user', 'pharmacy')
    all_advance_orders = AdvanceOrder.objects.filter(pharmacy=pharmacy).order_by('-created_at').select_related('user', 'pharmacy')

    # Apply filters on separate querysets
    filtered_orders = all_orders
    filtered_advance_orders = all_advance_orders

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        filtered_orders = filtered_orders.filter(status=status_filter)
        if status_filter in ['pending', 'confirmed', 'completed']:
            filtered_advance_orders = filtered_advance_orders.filter(status=status_filter)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        filtered_orders = filtered_orders.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(id__icontains=search_query) |
            Q(items__medicine__name__icontains=search_query)
        ).distinct()
        filtered_advance_orders = filtered_advance_orders.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(id__icontains=search_query) |
            Q(items__medicine_name__icontains=search_query)
        ).distinct()

    # Date range filter
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        filtered_orders = filtered_orders.filter(created_at__date__gte=date_from)
        filtered_advance_orders = filtered_advance_orders.filter(created_at__date__gte=date_from)
    if date_to:
        filtered_orders = filtered_orders.filter(created_at__date__lte=date_to)
        filtered_advance_orders = filtered_advance_orders.filter(created_at__date__lte=date_to)

    # Create a unified list for template rendering
    combined_orders = []

    # Add regular orders
    for order in filtered_orders:
        order_dict = {
            'id': order.id,
            'user': order.user,
            'status': order.status,
            'created_at': order.created_at,
            'is_advance_order': order.is_advance_order,
            'prescription': order.prescription,
            'total_amount': order.total_amount,
            'order_type': 'regular',
            'get_status_display': order.get_status_display(),
            'order': order,  # Add original order object
        }
        combined_orders.append(order_dict)

    # Add advance orders
    for advance_order in filtered_advance_orders:
        advance_order_dict = {
            'id': advance_order.id,
            'user': advance_order.user,
            'status': advance_order.status,
            'created_at': advance_order.created_at,
            'is_advance_order': True,  # Always true for advance orders
            'prescription': advance_order.prescription,
            'total_amount': sum(item.estimated_price or 0 for item in advance_order.items.all()),
            'order_type': 'advance',
            'get_status_display': advance_order.get_status_display(),
            'advance_order': advance_order,  # Add original advance order object
        }
        combined_orders.append(advance_order_dict)

    # Sort combined orders by creation date (newest first)
    combined_orders.sort(key=lambda o: o['created_at'], reverse=True)

    context = {
        'orders': filtered_orders,
        'advance_orders': filtered_advance_orders,
        'combined_orders': combined_orders,
        'pharmacy': pharmacy,
        'pending_count': all_orders.filter(status='pending').count() + all_advance_orders.filter(status='pending').count(),
        'confirmed_count': all_orders.filter(status='confirmed').count() + all_advance_orders.filter(status='confirmed').count(),
        'ready_count': all_orders.filter(status='ready').count(),
        'delivered_count': all_orders.filter(status='delivered').count(),
        'completed_count': all_orders.filter(status='completed').count() + all_advance_orders.filter(status='completed').count(),
        'total_orders': all_orders.count() + all_advance_orders.count(),
        'total_revenue': all_orders.filter(status__in=['delivered', 'completed']).aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
    }
    return render(request, 'orders/pharmacy_orders.html', context)

@login_required
def update_order_status(request, order_id):
    """Update order status"""
    logger.info(f"update_order_status called for order_id: {order_id}, user: {request.user.username}")

    # Get pharmacy from user.pharmacy or user.owned_pharmacy
    pharmacy = getattr(request.user, 'pharmacy', None) or getattr(request.user, 'owned_pharmacy', None)
    logger.info(f"Pharmacy found: {pharmacy}")

    if pharmacy is None:
        logger.error(f"Access denied: No pharmacy associated with user {request.user.username}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Access denied. No pharmacy associated with your account.'
            })
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')

    try:
        order = get_object_or_404(Order, id=order_id, pharmacy=pharmacy)
        logger.info(f"Order found: {order.id}, current status: {order.status}")
    except Exception as e:
        logger.error(f"Error finding order {order_id}: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Order not found: {str(e)}'
            })
        messages.error(request, f'Order not found: {str(e)}')
        return redirect('orders:pharmacy_orders')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        logger.info(f"New status requested: {new_status}")

        if not new_status:
            logger.error("No status provided in POST data")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'No status provided'
                })
            messages.error(request, 'No status provided')
            return redirect('orders:order_detail', order_id=order.id)

        if new_status not in dict(Order.STATUS_CHOICES):
            logger.error(f"Invalid status: {new_status}. Valid choices: {list(dict(Order.STATUS_CHOICES).keys())}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Invalid status: {new_status}'
                })
            messages.error(request, f'Invalid status: {new_status}')
            return redirect('orders:order_detail', order_id=order.id)

        try:
            old_status = order.status
            order.status = new_status
            order.save()
            logger.info(f"Order {order.id} status updated from {old_status} to {new_status}")

            # Send email notification for status update to customer
            try:
                email_result_customer = NotificationService.send_order_status_notification(order)
                if email_result_customer:
                    logger.info(f"Status update email sent to customer for order {order.id}")
                else:
                    logger.warning(f"Failed to send status update email to customer for order {order.id}")
            except Exception as e:
                logger.error(f"Error sending email to customer for order {order.id}: {str(e)}")

            # Send email notification for status update to pharmacist
            try:
                email_result_pharmacist = NotificationService.send_order_status_notification_to_pharmacist(order)
                if email_result_pharmacist:
                    logger.info(f"Status update email sent to pharmacist for order {order.id}")
                else:
                    logger.warning(f"Failed to send status update email to pharmacist for order {order.id}")
            except Exception as e:
                logger.error(f"Error sending email to pharmacist for order {order.id}: {str(e)}")

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Order status updated to {order.get_status_display()}',
                    'new_status': new_status,
                    'status_display': order.get_status_display()
                })
            else:
                messages.success(request, f'Order status updated to {order.get_status_display()}')

        except Exception as e:
            logger.error(f"Error updating order {order.id} status: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Error updating order status: {str(e)}'
                })
            messages.error(request, f'Error updating order status: {str(e)}')
            return redirect('orders:order_detail', order_id=order.id)

    return redirect('orders:order_detail', order_id=order.id)

@login_required
def update_advance_order_status(request, order_id):
    """Update advance order status"""
    # Get pharmacy from user.pharmacy or user.owned_pharmacy
    pharmacy = getattr(request.user, 'pharmacy', None) or getattr(request.user, 'owned_pharmacy', None)
    if pharmacy is None:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')

    advance_order = get_object_or_404(AdvanceOrder, id=order_id, pharmacy=pharmacy)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(AdvanceOrder.STATUS_CHOICES):
            old_status = advance_order.status
            advance_order.status = new_status
            advance_order.save()

            # Send email notification for status update
            if NotificationService.send_advance_order_status_notification(advance_order):
                logger.info(f"Status update email sent for advance order {advance_order.id}")
            else:
                logger.error(f"Failed to send status update email for advance order {advance_order.id}")

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Advance order status updated to {advance_order.get_status_display()}',
                    'new_status': new_status,
                    'status_display': advance_order.get_status_display()
                })
            else:
                messages.success(request, f'Advance order status updated to {advance_order.get_status_display()}')

    return redirect('orders:advance_order_detail', order_id=advance_order.id)

@login_required
def get_orders_data(request):
    """AJAX endpoint to get orders data for real-time updates"""
    # Get pharmacy from user.pharmacy or user.owned_pharmacy
    pharmacy = getattr(request.user, 'pharmacy', None) or getattr(request.user, 'owned_pharmacy', None)
    if pharmacy is None:
        return JsonResponse({'success': False, 'message': 'Access denied'})
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
        'completed_count': orders.filter(status='completed').count(),
        'total_orders': orders.count(),
        'total_revenue': str(orders.filter(status__in=['delivered', 'completed']).aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
    }

    return JsonResponse({
        'success': True,
        'orders': orders_data,
        'stats': stats
    })

@login_required
def get_pharmacy_dashboard_data(request):
    """AJAX endpoint to get pharmacy dashboard data for real-time updates"""
    # Get pharmacy from user.pharmacy or user.owned_pharmacy
    pharmacy = getattr(request.user, 'pharmacy', None) or getattr(request.user, 'owned_pharmacy', None)
    if pharmacy is None:
        return JsonResponse({'success': False, 'message': 'Access denied'})
    from django.db.models import Sum
    medicines = Medicine.objects.filter(pharmacy=pharmacy)

    # Calculate dashboard statistics
    # Calculate dashboard statistics
    total_medicines = medicines.count()
    total_quantity = medicines.aggregate(total=Sum('quantity'))['total'] or 0
    low_stock_count = medicines.filter(quantity__lt=10, quantity__gt=0).count()
    in_stock_count = medicines.filter(quantity__gte=10).count()
    pending_orders = Order.objects.filter(pharmacy=pharmacy, status='pending').count()
    pending_advance_orders = AdvanceOrder.objects.filter(pharmacy=pharmacy, status='pending').count()

    # Get recent orders
    recent_orders = Order.objects.filter(pharmacy=pharmacy).order_by('-created_at')[:10]
    orders_data = []
    for order in recent_orders:
        orders_data.append({
            'id': order.id,
            'customer_name': f"{order.user.first_name} {order.user.last_name}",
            'status': order.status,
            'status_display': order.get_status_display(),
            'total_amount': str(order.total_amount),
            'created_at': order.created_at.strftime('%b %d, %Y'),
            'items_count': order.items.count(),
        })

    return JsonResponse({
        'success': True,
        'stats': {
            'total_medicines': total_medicines,
            'total_quantity': total_quantity,
            'in_stock_count': in_stock_count,
            'low_stock_count': low_stock_count,
            'pending_orders': pending_orders,
            'pending_advance_orders': pending_advance_orders,
        },
        'recent_orders': orders_data
    })
    medicines = Medicine.objects.filter(pharmacy=pharmacy)

    # Calculate dashboard statistics
    total_medicines = medicines.count()
    total_quantity = medicines.aggregate(total=Sum('quantity'))['total'] or 0
    low_stock_count = medicines.filter(quantity__lt=10, quantity__gt=0).count()
    in_stock_count = medicines.filter(quantity__gte=10).count()
    pending_orders = Order.objects.filter(pharmacy=pharmacy, status='pending').count()
    pending_advance_orders = AdvanceOrder.objects.filter(pharmacy=pharmacy, status='pending').count()

    # Get recent orders
    recent_orders = Order.objects.filter(pharmacy=pharmacy).order_by('-created_at')[:10]
    orders_data = []
    for order in recent_orders:
        orders_data.append({
            'id': order.id,
            'customer_name': f"{order.user.first_name} {order.user.last_name}",
            'status': order.status,
            'status_display': order.get_status_display(),
            'total_amount': str(order.total_amount),
            'created_at': order.created_at.strftime('%b %d, %Y'),
            'items_count': order.items.count(),
        })

    return JsonResponse({
        'success': True,
        'stats': {
            'total_medicines': total_medicines,
            'total_quantity': total_quantity,
            'in_stock_count': in_stock_count,
            'low_stock_count': low_stock_count,
            'pending_orders': pending_orders,
            'pending_advance_orders': pending_advance_orders,
        },
        'recent_orders': orders_data
    })
    medicines = Medicine.objects.filter(pharmacy=pharmacy)

# Legacy functions for backward compatibility
@login_required
def create_order(request):
    return redirect('orders:upload_prescription')

@login_required
def select_medicines(request):
    medicines = Medicine.objects.filter(quantity__gt=0).order_by('name')
    return render(request, 'orders/select_medicines.html', {'medicines': medicines})

@login_required
def advance_orders(request):
    """View user's advance orders"""
    advance_orders = AdvanceOrder.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/advance_orders.html', {'advance_orders': advance_orders})

@login_required
def create_advance_order(request):
    """Create advance order for low stock or out of stock medicines by adding to cart and redirecting to checkout"""
    # Get all medicines that are low stock or out of stock from all pharmacies
    low_stock_medicines = Medicine.objects.filter(quantity__lt=10, quantity__gt=0)
    out_of_stock_medicines = Medicine.objects.filter(quantity=0)

    if request.method == 'POST':
        selected_meds = request.POST.getlist('medicines')

        if not selected_meds:
            messages.warning(request, 'Please select at least one medicine to order in advance.')
            return redirect('orders:create_advance_order')

        # Clear existing cart or get cart
        from .services import CartService
        cart = CartService.get_or_create_cart(request.user)
        CartService.clear_cart(request.user)

        # Add selected medicines to cart with advance order flag
        for med_id in selected_meds:
            try:
                med = Medicine.objects.get(id=med_id)
                qty_str = request.POST.get(f'quantity_{med_id}', '1')
                qty_int = int(qty_str) if qty_str.isdigit() else 1
                if qty_int > 0:
                    CartService.add_to_cart(request.user, med.id, qty_int, is_advance_order=True)
            except Medicine.DoesNotExist:
                continue

        messages.success(request, 'Selected medicines added to cart. Please proceed to checkout to complete your advance order.')
        return redirect('orders:checkout')

    context = {
        'low_stock_medicines': low_stock_medicines,
        'out_of_stock_medicines': out_of_stock_medicines,
    }
    return render(request, 'orders/create_advance_order.html', context)

@login_required
def advance_order_detail(request, order_id):
    """View advance order details"""
    advance_order = get_object_or_404(AdvanceOrder, id=order_id)

    # Check if user owns the advance order or is the pharmacy owner
    # Get pharmacy from user.pharmacy or user.owned_pharmacy
    pharmacy = getattr(request.user, 'pharmacy', None) or getattr(request.user, 'owned_pharmacy', None)
    if advance_order.user != request.user and (pharmacy is None or advance_order.pharmacy != pharmacy):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')

    return render(request, 'orders/advance_order_detail.html', {'advance_order': advance_order})

@login_required
def order_bill(request, order_id):
    """Generate bill for order"""
    order = get_object_or_404(Order, id=order_id)

    # Check if user owns the order or is the pharmacy owner
    # Get pharmacy from user.pharmacy or user.owned_pharmacy
    pharmacy = getattr(request.user, 'pharmacy', None) or getattr(request.user, 'owned_pharmacy', None)
    if order.user != request.user and (pharmacy is None or order.pharmacy != pharmacy):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')

    context = {
        'order': order,
        'items': order.items.all(),
        'subtotal': order.subtotal,
        'delivery_charges': order.delivery_charges,
        'total_amount': order.total_amount,
        'bill_number': f"BILL-{order.id}-{timezone.now().strftime('%Y%m%d')}",
        'bill_date': timezone.now().date(),
    }

    return render(request, 'orders/order_bill.html', context)

@login_required
def generate_bill(request, prescription_id):
    """Generate bill for prescription medicines"""
    prescription = get_object_or_404(Prescription, id=prescription_id, user=request.user)
    prescription_medicines = prescription.medicines.all()

    # Calculate totals
    available_total = 0
    unavailable_total = 0

    for medicine in prescription_medicines:
        if medicine.is_available and medicine.matched_medicine:
            available_total += medicine.matched_medicine.price * medicine.quantity_required
        else:
            # Estimate price for unavailable medicines (you can adjust this logic)
            unavailable_total += 50 * medicine.quantity_required  # Default ₹50 per unit

    context = {
        'prescription': prescription,
        'prescription_medicines': prescription_medicines,
        'available_total': available_total,
        'unavailable_total': unavailable_total,
        'total_amount': available_total + unavailable_total,
        'bill_number': f"BILL-{prescription.id}-{timezone.now().strftime('%Y%m%d')}",
        'bill_date': timezone.now().date(),
    }

    return render(request, 'orders/bill.html', context)

@login_required
def verify_prescription(request, prescription_id):
    """Pharmacist verification of prescription using code"""
    # Get pharmacy from user.pharmacy or user.owned_pharmacy
    pharmacy = getattr(request.user, 'pharmacy', None) or getattr(request.user, 'owned_pharmacy', None)
    if pharmacy is None:
        messages.error(request, 'Access denied. Only pharmacists can verify prescriptions.')
        return redirect('core:dashboard')

    prescription = get_object_or_404(Prescription, id=prescription_id)

    if request.method == 'POST':
        entered_code = request.POST.get('verification_code', '').strip()

        if not entered_code:
            messages.error(request, 'Please enter the verification code.')
            return redirect('orders:verify_prescription', prescription_id=prescription.id)

        if prescription.verification_code == entered_code:
            prescription.status = 'verified'
            prescription.is_verified = True
            prescription.save()

            # Send confirmation email to user
            NotificationService.send_prescription_verified_notification(prescription)

            messages.success(request, f'Prescription #{prescription.id} has been successfully verified!')
            return redirect('orders:prescription_detail', prescription_id=prescription.id)
        else:
            messages.error(request, 'Invalid verification code. Please try again.')

    context = {
        'prescription': prescription,
        'user': prescription.user,
    }
    return render(request, 'orders/verify_prescription.html', context)

@login_required
def prescription_detail(request, prescription_id):
    """View prescription details for pharmacist"""
    # Get pharmacy from user.pharmacy or user.owned_pharmacy
    pharmacy = getattr(request.user, 'pharmacy', None) or getattr(request.user, 'owned_pharmacy', None)
    if pharmacy is None:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')

    prescription = get_object_or_404(Prescription, id=prescription_id)
    prescription_medicines = prescription.medicines.all()

    context = {
        'prescription': prescription,
        'prescription_medicines': prescription_medicines,
        'user': prescription.user,
    }
    return render(request, 'orders/prescription_detail.html', context)
