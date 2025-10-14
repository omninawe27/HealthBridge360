import json
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from orders.models import Cart

@login_required
@require_POST
def create_razorpay_order(request):
    from orders.forms import CheckoutForm
    from decimal import Decimal
    import logging

    logger = logging.getLogger(__name__)

    try:
        cart = Cart.objects.get(user=request.user)
        if cart.item_count == 0:
            logger.error(f"Cart is empty for user {request.user.id}")
            return JsonResponse({'success': False, 'error': 'Cart is empty'})

        # Validate checkout form
        form = CheckoutForm(request.POST, initial={'user': request.user})
        if not form.is_valid():
            logger.error(f"Form validation failed for user {request.user.id}: {form.errors}")
            return JsonResponse({'success': False, 'error': 'Invalid form data', 'errors': form.errors})

        # Calculate delivery charges
        delivery_method = form.cleaned_data['delivery_method']
        delivery_charges = Decimal('50.00') if delivery_method == 'home_delivery' else Decimal('0.00')
        total_amount = cart.total_amount + delivery_charges
        amount = int(total_amount * 100)  # Razorpay expects paise

        logger.info(f"Creating Razorpay order for user {request.user.id}: subtotal={cart.total_amount}, delivery_charges={delivery_charges}, total={total_amount}")

        # Store form data in session for callback
        checkout_form_data = {
            'delivery_method': delivery_method,
            'delivery_address': form.cleaned_data.get('delivery_address', ''),
            'notes': form.cleaned_data.get('notes', ''),
            'payment_method': form.cleaned_data.get('payment_method', 'online'),
            'delivery_charges': str(delivery_charges),
            'subtotal': str(cart.total_amount),
            'total_amount': str(total_amount)
        }
        request.session['checkout_form_data'] = checkout_form_data
        request.session.modified = True

        # Check if Razorpay keys are configured
        if not hasattr(settings, 'RAZORPAY_KEY_ID') or not hasattr(settings, 'RAZORPAY_KEY_SECRET'):
            logger.error("Razorpay keys not configured")
            return JsonResponse({'success': False, 'error': 'Payment gateway not configured'})

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        data = {
            'amount': amount,
            'currency': 'INR',
            'payment_capture': 1,
            'notes': {
                'user_id': str(request.user.id),
                'checkout_data': json.dumps(checkout_form_data)
            }
        }
        razorpay_order = client.order.create(data=data)
        logger.info(f"Razorpay order created successfully: {razorpay_order['id']} for user {request.user.id}")
        return JsonResponse({
            'success': True,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'amount': amount,
            'currency': 'INR'
        })
    except Exception as e:
        logger.error(f"Error creating Razorpay order for user {request.user.id}: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': f'Failed to initiate payment: {str(e)}'})


@csrf_exempt
@require_POST
def razorpay_callback(request):
    import json
    import logging
    from django.urls import reverse
    from django.core.mail import send_mail
    from django.conf import settings as django_settings
    from orders.models import Cart, Order, OrderItem
    from orders.forms import CheckoutForm
    from notifications.services import NotificationService
    from django.contrib.auth import get_user_model

    logger = logging.getLogger(__name__)

    data = json.loads(request.body)
    payment_id = data.get('razorpay_payment_id')
    order_id = data.get('razorpay_order_id')
    signature = data.get('razorpay_signature')

    logger.info(f"Razorpay callback received: payment_id={payment_id}, order_id={order_id}")

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })
        logger.info(f"Payment signature verified for order {order_id}")
        # Get user and checkout data from Razorpay order notes
        order_details = client.order.fetch(order_id)
        notes = order_details.get('notes', {})
        user_id = notes.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'error': 'User ID not found in order notes.'})
        User = get_user_model()
        user = User.objects.get(pk=user_id)

        checkout_data_str = notes.get('checkout_data')
        if not checkout_data_str:
            return JsonResponse({'success': False, 'error': 'Checkout data not found in order notes.'})
        checkout_data = json.loads(checkout_data_str)

        # Place order for this user
        cart = Cart.objects.get(user=user)
        if cart.item_count == 0:
            return JsonResponse({'success': False, 'error': 'Cart is empty.'})

        # Determine pharmacy
        pharmacy = cart.items.first().medicine.pharmacy

        # Check if cart contains advance order items
        has_advance_order_items = cart.items.filter(is_advance_order=True).exists()

        # Create order
        from decimal import Decimal
        order = Order.objects.create(
            user=user,
            pharmacy=pharmacy,
            status='confirmed',
            payment_method=checkout_data['payment_method'],
            delivery_method=checkout_data['delivery_method'],
            delivery_address=checkout_data.get('delivery_address', ''),
            notes=checkout_data.get('notes', ''),
            delivery_charges=Decimal(checkout_data['delivery_charges']),
            total_amount=Decimal(checkout_data['total_amount'])
        )

        # Mark as advance order if cart contains advance order items
        if has_advance_order_items:
            order.is_advance_order = True
            order.advance_order_type = 'restock'
            order.save()

        # Create order items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                medicine=item.medicine,
                quantity=item.quantity,
                price=item.medicine.price
            )
            # Only update medicine stock for non-advance order items
            if not item.is_advance_order:
                item.medicine.quantity -= item.quantity
                item.medicine.save()

        # Calculate totals (though we set them manually)
        order.calculate_totals()

        # Create AdvanceOrder record if this is an advance order
        if has_advance_order_items:
            from orders.models import AdvanceOrder, AdvanceOrderItem
            advance_order = AdvanceOrder.objects.create(
                user=user,
                pharmacy=pharmacy,
                order_type='restock',
                status='confirmed'  # Since payment is done
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
            if NotificationService.send_advance_order_notification(advance_order):
                pass  # logged in service
            else:
                pass  # logged

            # Send verification code to pharmacist for advance order
            if NotificationService.send_order_verification_code(advance_order):
                pass
            else:
                pass

            # Send verification code to customer for advance order
            if NotificationService.send_customer_order_verification_code(advance_order):
                pass
            else:
                pass

        # Clear cart
        cart.items.all().delete()

        # Send order status notification emails to customer
        if NotificationService.send_order_status_notification(order):
            pass
        else:
            pass

        # Send order notification to pharmacist
        if NotificationService.send_order_notification_to_pharmacist(order):
            pass
        else:
            pass

        # Send verification code to pharmacist for normal order
        if NotificationService.send_order_verification_code(order):
            pass
        else:
            pass

        # Send verification code to customer for normal order
        if NotificationService.send_customer_order_verification_code(order):
            pass
        else:
            pass

        # Clear session data
        if 'checkout_form_data' in request.session:
            del request.session['checkout_form_data']

        logger.info(f"Order {order.id} created successfully for user {user.id}, redirecting to order detail")
        return JsonResponse({'success': True, 'redirect_url': reverse('orders:order_detail', args=[order.id])})
    except Exception as e:
        logger.error(f"Error in Razorpay callback: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)})
