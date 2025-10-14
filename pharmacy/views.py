import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import PharmacyRegistrationForm
from .models import Pharmacy
from users.models import User
from medicines.models import Medicine
from orders.models import Order, AdvanceOrder

logger = logging.getLogger(__name__)

def pharmacy_register(request):
    if request.method == 'POST':
        form = PharmacyRegistrationForm(request.POST)
        if form.is_valid():
            # Create user account
            user = User.objects.create_user(
                username=form.cleaned_data['owner_username'],
                first_name=form.cleaned_data['owner_first_name'],
                last_name=form.cleaned_data['owner_last_name'],
                phone_number=form.cleaned_data['owner_phone'],
                password=form.cleaned_data['owner_password'],
                email=form.cleaned_data['owner_email'],
                is_pharmacist=True
            )
            
            # Create pharmacy
            pharmacy = form.save(commit=False)
            pharmacy.owner = user
            pharmacy.save()
            
            messages.success(request, 'Pharmacy registered successfully!')
            return redirect('users:login')
    else:
        form = PharmacyRegistrationForm()
    
    return render(request, 'pharmacy/register.html', {'form': form})

@login_required
def pharmacy_dashboard(request):
    # Get pharmacy from user.pharmacy or user.owned_pharmacy
    pharmacy = getattr(request.user, 'pharmacy', None) or getattr(request.user, 'owned_pharmacy', None)
    if pharmacy is None:
        messages.error(request, 'Access denied. Pharmacist account required.')
        return redirect('core:dashboard')

    from django.core.cache import cache
    from django.db.models import Sum

    # Cache dashboard data for 5 minutes
    cache_key = f'pharmacy_dashboard_{pharmacy.id}'
    cached_data = cache.get(cache_key)

    if cached_data:
        context = cached_data
    else:
        medicines = Medicine.objects.filter(pharmacy=pharmacy)
        total_medicines = medicines.count()  # Number of medicine types
        total_quantity = medicines.aggregate(total=Sum('quantity'))['total'] or 0  # Sum of all quantities
        low_stock_count = medicines.filter(quantity__lt=10, quantity__gt=0).count()
        in_stock_count = medicines.filter(quantity__gte=10).count()
        out_of_stock_count = medicines.filter(quantity=0).count()
        pending_orders = Order.objects.filter(pharmacy=pharmacy, status='pending').count()
        pending_advance_orders = AdvanceOrder.objects.filter(pharmacy=pharmacy, status='pending').count()
        recent_orders = Order.objects.filter(pharmacy=pharmacy).order_by('-created_at').select_related('user')[:10]
        recent_advance_orders = AdvanceOrder.objects.filter(pharmacy=pharmacy).order_by('-created_at').select_related('user')[:10]

        context = {
            'pharmacy': pharmacy,
            'total_medicines': total_medicines,
            'total_quantity': total_quantity,
            'low_stock_count': low_stock_count,
            'in_stock_count': in_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'pending_orders': pending_orders,
            'pending_advance_orders': pending_advance_orders,
            'recent_orders': recent_orders,
            'recent_advance_orders': recent_advance_orders,
        }
        # Cache for 5 minutes
        cache.set(cache_key, context, 300)

    return render(request, 'pharmacy/dashboard.html', context)

@login_required
def manage_inventory(request):
    # Get pharmacy from user.pharmacy or user.owned_pharmacy
    pharmacy = getattr(request.user, 'pharmacy', None) or getattr(request.user, 'owned_pharmacy', None)
    if pharmacy is None:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')

    from django.core.cache import cache
    from django.core.paginator import Paginator

    # Cache counts for 10 minutes
    counts_cache_key = f'inventory_counts_{pharmacy.id}'
    cached_counts = cache.get(counts_cache_key)

    if cached_counts:
        in_stock_count, out_of_stock_count, low_stock_count = cached_counts
    else:
        medicines_queryset = Medicine.objects.filter(pharmacy=pharmacy)
        in_stock_count = medicines_queryset.filter(quantity__gte=10).count()
        out_of_stock_count = medicines_queryset.filter(quantity=0).count()
        low_stock_count = medicines_queryset.filter(quantity__lt=10, quantity__gt=0).count()
        cache.set(counts_cache_key, (in_stock_count, out_of_stock_count, low_stock_count), 600)

    # Paginate medicines for better performance
    medicines = Medicine.objects.filter(pharmacy=pharmacy).order_by('name')
    paginator = Paginator(medicines, 50)  # 50 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'pharmacy': pharmacy,
        'medicines': page_obj,
        'in_stock_count': in_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'low_stock_count': low_stock_count,
    }
    return render(request, 'medicines/inventory.html', context)

@login_required
def pharmacy_profile(request):
    # Get pharmacy from user.pharmacy or user.owned_pharmacy
    pharmacy = getattr(request.user, 'pharmacy', None) or getattr(request.user, 'owned_pharmacy', None)
    if pharmacy is None:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')

    if request.method == 'POST':
        new_name = request.POST.get('name')
        if new_name:
            pharmacy.name = new_name
            pharmacy.save()
            messages.success(request, 'Pharmacy name updated successfully!')
        return redirect('pharmacy:profile')

    context = {
        'pharmacy': pharmacy,
    }
    return render(request, 'pharmacy/profile.html', context)

def welcome(request):
    """
    Returns a welcome message as JSON and logs the request.
    """
    logger.info(f"Request received: {request.method} {request.path}")
    return JsonResponse({'message': 'Welcome to the Pharmacy App!'})
