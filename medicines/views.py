from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.template.loader import render_to_string
from .models import Medicine, MedicineAlternative
from .forms import MedicineForm

@login_required
def add_medicine(request):
    # Get pharmacy from user.pharmacy or user.owned_pharmacy
    pharmacy = getattr(request.user, 'pharmacy', None) or getattr(request.user, 'owned_pharmacy', None)
    if pharmacy is None:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            medicine = form.save(commit=False)
            medicine.pharmacy = pharmacy
            medicine.save()
            messages.success(request, 'Medicine added successfully!')
            return redirect('medicines:inventory')
    else:
        form = MedicineForm()

    return render(request, 'medicines/add_medicine.html', {'form': form})

@login_required
def edit_medicine(request, medicine_id):
    # Get pharmacy from user.pharmacy or user.owned_pharmacy
    pharmacy = getattr(request.user, 'pharmacy', None) or getattr(request.user, 'owned_pharmacy', None)
    if pharmacy is None:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')

    medicine = get_object_or_404(Medicine, id=medicine_id, pharmacy=pharmacy)

    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine updated successfully!')
            return redirect('medicines:inventory')
    else:
        form = MedicineForm(instance=medicine)

    return render(request, 'medicines/edit_medicine.html', {'form': form, 'medicine': medicine})

@login_required
def delete_medicine(request, medicine_id):
    # Get pharmacy from user.pharmacy or user.owned_pharmacy
    pharmacy = getattr(request.user, 'pharmacy', None) or getattr(request.user, 'owned_pharmacy', None)
    if pharmacy is None:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')

    medicine = get_object_or_404(Medicine, id=medicine_id, pharmacy=pharmacy)

    if request.method == 'POST':
        medicine.delete()
        messages.success(request, 'Medicine deleted successfully!')
        return redirect('medicines:inventory')

    return render(request, 'medicines/delete_medicine.html', {'medicine': medicine})

@login_required
def delete_medicine_ajax(request, medicine_id):
    """AJAX endpoint to delete medicine"""
    # Get pharmacy from user.pharmacy or user.owned_pharmacy
    pharmacy = getattr(request.user, 'pharmacy', None) or getattr(request.user, 'owned_pharmacy', None)
    if pharmacy is None:
        return JsonResponse({'success': False, 'message': 'Access denied'})

    if request.method == 'POST':
        try:
            medicine = get_object_or_404(Medicine, id=medicine_id, pharmacy=pharmacy)
            medicine_name = medicine.name
            medicine.delete()

            return JsonResponse({
                'success': True,
                'message': f'{medicine_name} deleted successfully!'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def search_alternatives(request):
    medicine_id = request.GET.get('medicine_id')
    if medicine_id:
        try:
            medicine = Medicine.objects.get(id=medicine_id)
            alternatives = Medicine.objects.filter(
                generic_name=medicine.generic_name,
                quantity__gt=0
            ).exclude(id=medicine_id)
            
            data = [{
                'id': alt.id,
                'name': alt.name,
                'brand': alt.brand,
                'price': str(alt.price),
                'pharmacy': alt.pharmacy.name,
                'status': alt.status_display
            } for alt in alternatives]
            
            return JsonResponse({'alternatives': data})
        except Medicine.DoesNotExist:
            pass
    
    return JsonResponse({'alternatives': []})

@login_required
def get_alternatives(request, medicine_id):
    """Get alternatives for a specific medicine"""
    try:
        medicine = get_object_or_404(Medicine, id=medicine_id)
        alternatives = Medicine.objects.filter(
            Q(generic_name=medicine.generic_name) | Q(name__icontains=medicine.name),
            quantity__gt=0
        ).exclude(id=medicine_id)[:10]
        
        html = render_to_string(
            'medicines/alternatives_list.html',
            {
                'alternatives': alternatives,
                'original_medicine': medicine
            },
            request=request
        )
        
        return JsonResponse({'html': html, 'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def inventory(request):
    """Pharmacy inventory management"""
    # Get pharmacy from user.pharmacy or user.owned_pharmacy
    pharmacy = getattr(request.user, 'pharmacy', None) or getattr(request.user, 'owned_pharmacy', None)
    if pharmacy is None:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')

    from django.core.paginator import Paginator
    from django.core.cache import cache

    # Base queryset
    medicines = Medicine.objects.filter(pharmacy=pharmacy)

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        if status_filter == 'low_stock':
            medicines = medicines.filter(quantity__lt=10)
        elif status_filter == 'out_of_stock':
            medicines = medicines.filter(quantity=0)
        elif status_filter == 'expiring_soon':
            from django.utils import timezone
            from datetime import timedelta
            medicines = medicines.filter(expiry_date__lte=timezone.now().date() + timedelta(days=30))

    # Cache counts for 10 minutes
    counts_cache_key = f'inventory_counts_{pharmacy.id}_{status_filter or "all"}'
    cached_counts = cache.get(counts_cache_key)

    if cached_counts:
        total_medicines, in_stock_count, low_stock_count, out_of_stock_count = cached_counts
    else:
        total_medicines = medicines.count()
        all_medicines = Medicine.objects.filter(pharmacy=pharmacy)
        in_stock_count = all_medicines.filter(quantity__gte=10).count()
        low_stock_count = all_medicines.filter(quantity__lt=10, quantity__gt=0).count()
        out_of_stock_count = all_medicines.filter(quantity=0).count()
        cache.set(counts_cache_key, (total_medicines, in_stock_count, low_stock_count, out_of_stock_count), 600)

    # Paginate results
    medicines = medicines.order_by('name')
    paginator = Paginator(medicines, 50)  # 50 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'pharmacy': pharmacy,
        'medicines': page_obj,
        'total_medicines': total_medicines,
        'in_stock_count': in_stock_count,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'status_filter': status_filter,
    }
    return render(request, 'medicines/inventory.html', context)

@login_required
def update_stock(request, medicine_id):
    """AJAX endpoint to update medicine stock"""
    # Get pharmacy from user.pharmacy or user.owned_pharmacy
    pharmacy = getattr(request.user, 'pharmacy', None) or getattr(request.user, 'owned_pharmacy', None)
    if pharmacy is None:
        return JsonResponse({'success': False, 'message': 'Access denied - no pharmacy associated'})

    if request.method == 'POST':
        try:
            import json
            medicine = get_object_or_404(Medicine, id=medicine_id, pharmacy=pharmacy)
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                quantity = int(data.get('quantity', medicine.quantity))
                price = float(data.get('price', medicine.price or 0))
            else:
                quantity = int(request.POST.get('quantity', medicine.quantity))
                price = float(request.POST.get('price', medicine.price or 0))
            medicine.quantity = quantity
            medicine.price = price
            medicine.save()
            return JsonResponse({
                'success': True,
                'message': 'Stock updated successfully',
                'new_quantity': quantity,
                'new_price': str(price),
                'status': medicine.status_display
            })
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'message': 'Invalid data provided'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def medicine_details(request, medicine_id):
    """Get detailed information about a medicine"""
    try:
        medicine = get_object_or_404(Medicine, id=medicine_id)

        # Get pharmacy from user.pharmacy or user.owned_pharmacy
        user_pharmacy = getattr(request.user, 'pharmacy', None) or getattr(request.user, 'owned_pharmacy', None)

        # Check if user has access to this medicine
        if user_pharmacy is None or medicine.pharmacy != user_pharmacy:
            return JsonResponse({'success': False, 'message': 'Access denied'})

        data = {
            'id': medicine.id,
            'name': medicine.name,
            'generic_name': medicine.generic_name,
            'brand': medicine.brand,
            'medicine_type': medicine.get_medicine_type_display(),
            'strength': medicine.strength,
            'price': str(medicine.price),
            'quantity': medicine.quantity,
            'expiry_date': medicine.expiry_date.strftime('%Y-%m-%d'),
            'batch_number': medicine.batch_number,
            'is_essential': medicine.is_essential,
            'is_prescription_required': medicine.is_prescription_required,
            'status': medicine.status_display,
            'pharmacy_name': medicine.pharmacy.name,
            'pharmacy_address': medicine.pharmacy.address,
            'pharmacy_phone': medicine.pharmacy.phone_number,
        }

        return JsonResponse({'success': True, 'medicine': data})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def bulk_update_stock(request):
    """Bulk update medicine stock"""
    # Get pharmacy from user.pharmacy or user.owned_pharmacy
    pharmacy = getattr(request.user, 'pharmacy', None) or getattr(request.user, 'owned_pharmacy', None)
    if pharmacy is None:
        return JsonResponse({'success': False, 'message': 'Access denied'})

    if request.method == 'POST':
        try:
            updates = request.POST.getlist('updates[]')
            updated_count = 0

            for update in updates:
                medicine_id, quantity, price = update.split(',')
                medicine = get_object_or_404(Medicine, id=medicine_id, pharmacy=pharmacy)
                medicine.quantity = int(quantity)
                medicine.price = float(price)
                medicine.save()
                updated_count += 1

            return JsonResponse({
                'success': True,
                'message': f'{updated_count} medicines updated successfully'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})
