from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import PharmacyRegistrationForm
from .models import Pharmacy
from users.models import User
from medicines.models import Medicine
from orders.models import Order

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
    if not hasattr(request.user, 'pharmacy'):
        messages.error(request, 'Access denied. Pharmacist account required.')
        return redirect('core:dashboard')
    
    pharmacy = request.user.pharmacy
    context = {
        'pharmacy': pharmacy,
        'total_medicines': Medicine.objects.filter(pharmacy=pharmacy).count(),
        'low_stock_count': Medicine.objects.filter(pharmacy=pharmacy, quantity__lt=10).count(),
        'pending_orders': Order.objects.filter(pharmacy=pharmacy, status='pending').count(),
        'recent_orders': Order.objects.filter(pharmacy=pharmacy).order_by('-created_at')[:10],
    }
    return render(request, 'pharmacy/dashboard.html', context)

@login_required
def manage_inventory(request):
    if not hasattr(request.user, 'pharmacy'):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    pharmacy = request.user.pharmacy
    medicines = Medicine.objects.filter(pharmacy=pharmacy).order_by('name')
    
    context = {
        'pharmacy': pharmacy,
        'medicines': medicines,
    }
    return render(request, 'pharmacy/inventory.html', context)

@login_required
def pharmacy_profile(request):
    if not hasattr(request.user, 'pharmacy'):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    pharmacy = request.user.pharmacy
    context = {
        'pharmacy': pharmacy,
    }
    return render(request, 'pharmacy/profile.html', context)
