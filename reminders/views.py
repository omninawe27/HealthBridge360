from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Reminder
from .forms import ReminderForm
from notifications.services import NotificationService

@login_required
def reminder_list(request):
    reminders = Reminder.objects.filter(user=request.user).order_by('time_slot', 'specific_time')
    
    # Group reminders by time slot
    grouped_reminders = {
        'morning': reminders.filter(time_slot='morning'),
        'afternoon': reminders.filter(time_slot='afternoon'),
        'evening': reminders.filter(time_slot='evening'),
        'night': reminders.filter(time_slot='night'),
    }
    
    context = {
        'reminders': reminders,
        'grouped_reminders': grouped_reminders,
        'active_count': reminders.filter(is_active=True).count(),
        'total_count': reminders.count(),
    }
    return render(request, 'reminders/list.html', context)

@login_required
def add_reminder(request):
    if request.method == 'POST':
        form = ReminderForm(request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.user = request.user
            reminder.save()
            messages.success(request, 'Reminder added successfully!')
            return redirect('reminders:list')
    else:
        form = ReminderForm()
    
    return render(request, 'reminders/add.html', {'form': form})

@login_required
def edit_reminder(request, reminder_id):
    reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
    
    if request.method == 'POST':
        form = ReminderForm(request.POST, instance=reminder)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reminder updated successfully!')
            return redirect('reminders:list')
    else:
        form = ReminderForm(instance=reminder)
    
    return render(request, 'reminders/edit.html', {'form': form, 'reminder': reminder})

@login_required
def delete_reminder(request, reminder_id):
    reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
    
    if request.method == 'POST':
        reminder.delete()
        messages.success(request, 'Reminder deleted successfully!')
        return redirect('reminders:list')
    
    return render(request, 'reminders/delete.html', {'reminder': reminder})

@login_required
def toggle_reminder(request, reminder_id):
    reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
    reminder.is_active = not reminder.is_active
    reminder.save()
    
    status = "activated" if reminder.is_active else "deactivated"
    messages.success(request, f'Reminder {status} successfully!')
    return redirect('reminders:list')

@login_required
def toggle_reminder_ajax(request, reminder_id):
    """AJAX endpoint to toggle reminder status"""
    if request.method == 'POST':
        try:
            reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
            reminder.is_active = not reminder.is_active
            reminder.save()
            
            return JsonResponse({
                'success': True,
                'is_active': reminder.is_active,
                'message': f'Reminder {"activated" if reminder.is_active else "deactivated"} successfully!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def add_reminder_ajax(request):
    """AJAX endpoint to add reminder"""
    if request.method == 'POST':
        try:
            form = ReminderForm(request.POST)
            if form.is_valid():
                reminder = form.save(commit=False)
                reminder.user = request.user
                reminder.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Reminder added successfully!',
                    'reminder_id': reminder.id
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Please correct the errors below.',
                    'errors': form.errors
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def get_due_reminders(request):
    """Get reminders that are due now"""
    now = timezone.now()
    current_hour = now.hour
    
    # Determine current time slot
    if 6 <= current_hour < 12:
        current_slot = 'morning'
    elif 12 <= current_hour < 17:
        current_slot = 'afternoon'
    elif 17 <= current_hour < 21:
        current_slot = 'evening'
    else:
        current_slot = 'night'
    
    # Get due reminders
    due_reminders = Reminder.objects.filter(
        user=request.user,
        is_active=True,
        time_slot=current_slot
    )
    
    reminder_data = []
    for reminder in due_reminders:
        reminder_data.append({
            'id': reminder.id,
            'medicine_name': reminder.medicine_name,
            'time_slot': reminder.get_time_slot_display(),
            'notes': reminder.notes,
            'alert_type': reminder.get_alert_type_display()
        })
    
    return JsonResponse({
        'success': True,
        'due_reminders': reminder_data,
        'current_slot': current_slot
    })

@login_required
def mark_reminder_taken(request, reminder_id):
    """Mark a reminder as taken"""
    if request.method == 'POST':
        try:
            reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
            
            # Create a record of taking the medicine
            # This could be extended to track medicine adherence
            
            return JsonResponse({
                'success': True,
                'message': f'Marked {reminder.medicine_name} as taken!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def reminder_statistics(request):
    """Get reminder statistics for the user"""
    reminders = Reminder.objects.filter(user=request.user)
    
    stats = {
        'total_reminders': reminders.count(),
        'active_reminders': reminders.filter(is_active=True).count(),
        'morning_reminders': reminders.filter(time_slot='morning').count(),
        'afternoon_reminders': reminders.filter(time_slot='afternoon').count(),
        'evening_reminders': reminders.filter(time_slot='evening').count(),
        'night_reminders': reminders.filter(time_slot='night').count(),
    }
    
    return JsonResponse({
        'success': True,
        'statistics': stats
    })

@login_required
def bulk_actions(request):
    """Perform bulk actions on reminders"""
    if request.method == 'POST':
        action = request.POST.get('action')
        reminder_ids = request.POST.getlist('reminder_ids')
        
        if not reminder_ids:
            return JsonResponse({
                'success': False,
                'message': 'No reminders selected'
            })
        
        reminders = Reminder.objects.filter(id__in=reminder_ids, user=request.user)
        
        if action == 'activate':
            reminders.update(is_active=True)
            message = f'{reminders.count()} reminders activated'
        elif action == 'deactivate':
            reminders.update(is_active=False)
            message = f'{reminders.count()} reminders deactivated'
        elif action == 'delete':
            count = reminders.count()
            reminders.delete()
            message = f'{count} reminders deleted'
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid action'
            })
        
        return JsonResponse({
            'success': True,
            'message': message
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def test_notification(request, reminder_id):
    """Test notification for a specific reminder"""
    if request.method == 'POST':
        try:
            reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
            
            # Send test notifications
            notifications_sent = NotificationService.send_reminder_notifications(reminder)
            
            return JsonResponse({
                'success': True,
                'message': f'Test notification sent! ({notifications_sent} notifications delivered)'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})
