from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import translation
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from medicines.models import Medicine
from pharmacy.models import Pharmacy
from orders.models import Order
from reminders.models import Reminder
from django.utils import timezone
from django.conf import settings

def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    """User dashboard view"""
    try:
        context = {}
        
        # Check if user is a pharmacist by looking for pharmacy ownership
        try:
            pharmacy = request.user.pharmacy
            is_pharmacist = True
        except Pharmacy.DoesNotExist:
            is_pharmacist = False
            pharmacy = None
        
        if is_pharmacist:
            context.update({
                'is_pharmacist': True,
                'pharmacy': pharmacy,
                'pending_orders': Order.objects.filter(pharmacy=pharmacy, status='pending').count(),
                'low_stock_medicines': Medicine.objects.filter(pharmacy=pharmacy, quantity__lt=10).count(),
                'in_stock_medicines': Medicine.objects.filter(pharmacy=pharmacy, quantity__gt=0).count(),
                'recent_orders': Order.objects.filter(pharmacy=pharmacy).order_by('-created_at')[:5],
            })
            return render(request, 'core/pharmacist_dashboard.html', context)
        else:
            # User dashboard
            context.update({
                'is_pharmacist': False,
                'recent_orders': Order.objects.filter(user=request.user).order_by('-created_at')[:5],
                'active_reminders': Reminder.objects.filter(user=request.user, is_active=True).count(),
                'pending_orders': Order.objects.filter(user=request.user, status='pending').count(),
            })
            return render(request, 'core/user_dashboard.html', context)
    except Exception as e:
        # Log the error and return a simple error page
        print(f"Dashboard error: {e}")
        return render(request, 'core/error.html', {'error': str(e)})

def change_language(request):
    """Change language view"""
    if request.method == 'POST':
        language = request.POST.get('language')
        if language:
            # Set language in session
            request.session[translation.LANGUAGE_SESSION_KEY] = language
            # Set language for current request
            translation.activate(language)
            
            # Save user preference if logged in
            if request.user.is_authenticated:
                request.user.preferred_language = language
                request.user.save()
            
            messages.success(request, f'Language changed to {dict(settings.LANGUAGES).get(language, language)}')
    
    # Redirect back to the previous page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def emergency_mode(request):
    """Emergency mode - show 24x7 pharmacies"""
    emergency_pharmacies = Pharmacy.objects.filter(is_24x7=True, is_active=True)
    essential_medicines = Medicine.objects.filter(is_essential=True, quantity__gt=0)
    
    context = {
        'emergency_pharmacies': emergency_pharmacies,
        'essential_medicines': essential_medicines,
    }
    return render(request, 'core/emergency.html', context)

@login_required
def search_medicines(request):
    """Search medicines and pharmacies"""
    query = request.GET.get('q', '')
    medicines = []
    pharmacies = []
    
    if query:
        medicines = Medicine.objects.filter(
            Q(name__icontains=query) | Q(generic_name__icontains=query),
            quantity__gt=0
        ).select_related('pharmacy')
        
        pharmacies = Pharmacy.objects.filter(
            Q(name__icontains=query) | Q(address__icontains=query),
            is_active=True
        )
    
    context = {
        'query': query,
        'medicines': medicines,
        'pharmacies': pharmacies,
    }
    return render(request, 'core/search.html', context)
