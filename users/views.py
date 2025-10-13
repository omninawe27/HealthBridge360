from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from .forms import UserRegistrationForm, UserLoginForm

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('users:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect pharmacists to pharmacy dashboard
                if hasattr(user, 'is_pharmacist') and user.is_pharmacist:
                    return redirect('pharmacy:dashboard')
                return redirect('core:dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        # Update profile information
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.preferred_language = request.POST.get('preferred_language', user.preferred_language)

        # Handle pharmacy name update for pharmacists
        if hasattr(user, 'is_pharmacist') and user.is_pharmacist:
            pharmacy = getattr(user, 'pharmacy', None) or getattr(user, 'owned_pharmacy', None)
            if pharmacy:
                pharmacy_name = request.POST.get('pharmacy_name')
                if pharmacy_name:
                    pharmacy.name = pharmacy_name
                    pharmacy.save()

        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']

        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('users:profile')

    # Get pharmacy for pharmacists
    pharmacy = None
    if hasattr(request.user, 'is_pharmacist') and request.user.is_pharmacist:
        pharmacy = getattr(request.user, 'pharmacy', None) or getattr(request.user, 'owned_pharmacy', None)

    return render(request, 'users/profile.html', {'user': request.user, 'pharmacy': pharmacy})

@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        user = request.user

        if not user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
        elif new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
        elif len(new_password1) < 8:
            messages.error(request, 'New password must be at least 8 characters.')
        else:
            user.set_password(new_password1)
            user.save()
            messages.success(request, 'Password changed successfully.')
            return redirect('users:profile')

        # If error, redirect back to profile and open modal
        return redirect('users:profile')  # Always redirect to profile

    return redirect('users:profile')

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Account deleted successfully.')
        return redirect('core:home')
    
    return render(request, 'users/delete_account.html')

@login_required
def update_profile_ajax(request):
    """AJAX endpoint for updating profile"""
    if request.method == 'POST':
        try:
            user = request.user
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.phone_number = request.POST.get('phone_number', user.phone_number)
            user.preferred_language = request.POST.get('preferred_language', user.preferred_language)
            user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Profile updated successfully!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})
