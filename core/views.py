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
from .utils import sanitize_cache_key
import logging

logger = logging.getLogger(__name__)

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

        # Check if user is a pharmacist using the is_pharmacist field
        pharmacy = getattr(request.user, 'pharmacy', None) or getattr(request.user, 'owned_pharmacy', None)
        if request.user.is_pharmacist and pharmacy:
            # Redirect pharmacists to their dedicated pharmacy dashboard
            return redirect('pharmacy:dashboard')
        else:
            # User dashboard
            context.update({
                'is_pharmacist': False,
                'recent_orders': Order.objects.filter(user=request.user).order_by('-created_at').select_related('pharmacy')[:5],
                'active_reminders': Reminder.objects.filter(user=request.user, is_active=True).count(),
                'pending_orders': Order.objects.filter(user=request.user, status='pending').count(),
                'confirmed_orders': Order.objects.filter(user=request.user, status='confirmed').count(),
                'ready_orders': Order.objects.filter(user=request.user, status='ready').count(),
                'delivered_orders': Order.objects.filter(user=request.user, status='delivered').count(),
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
        if language and language in [lang[0] for lang in settings.LANGUAGES]:
            # Set language in session using correct key
            request.session['django_language'] = language
            # Set language for current request
            translation.activate(language)
            
            # Save user preference if logged in
            if hasattr(request, 'user') and request.user.is_authenticated:
                try:
                    request.user.preferred_language = language
                    request.user.save()
                except Exception as e:
                    # Log error but don't break the request
                    print(f"Error saving user language preference: {e}")
            
            messages.success(request, f'Language changed to {dict(settings.LANGUAGES).get(language, language)}')
    
    # Redirect back to the previous page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def emergency_mode(request):
    """Emergency mode - show 24x7 pharmacies"""
    from django.core.cache import cache
    cache_key = 'emergency_mode_data'
    cached_data = cache.get(cache_key)

    if cached_data:
        context = cached_data
    else:
        emergency_pharmacies = Pharmacy.objects.filter(is_24x7=True, is_active=True).select_related()
        essential_medicines = Medicine.objects.filter(is_essential=True, quantity__gt=0).select_related('pharmacy')[:50]  # Limit to 50 for performance

        context = {
            'emergency_pharmacies': emergency_pharmacies,
            'essential_medicines': essential_medicines,
        }
        # Cache for 15 minutes
        cache.set(cache_key, context, 900)

    return render(request, 'core/emergency.html', context)

@login_required
def search_medicines(request):
    """Search medicines and pharmacies"""
    from django.core.cache import cache

    query = request.GET.get('q', '')
    medicines = []
    pharmacies = []

    if query:
        # Cache search results for 5 minutes
        cache_key = f'search_query_{sanitize_cache_key(query.lower().strip())}'
        cached_results = cache.get(cache_key)

        if cached_results:
            medicines, pharmacies = cached_results
        else:
            medicines = Medicine.objects.filter(
                Q(name__icontains=query) | Q(generic_name__icontains=query),
                quantity__gt=0
            ).select_related('pharmacy')[:20]  # Limit results for performance

            pharmacies = Pharmacy.objects.filter(
                Q(name__icontains=query) | Q(address__icontains=query),
                is_active=True
            )[:10]  # Limit results for performance

            # Cache for 5 minutes
            cache.set(cache_key, (medicines, pharmacies), 300)

    context = {
        'query': query,
        'medicines': medicines,
        'pharmacies': pharmacies,
    }
    return render(request, 'core/search.html', context)

def welcome_api(request):
    """API endpoint that logs requests and returns a welcome message"""
    # Log request metadata
    logger.info(f"API request received: {request.method} {request.path}")

    # Return JSON response with welcome message
    return JsonResponse({
        'message': 'Welcome to HealthKart 360 API!'
    })

