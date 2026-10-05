from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone

from .models import User, Role, LoyaltyPointsLedger
from .forms import CustomerRegistrationForm, CustomerLoginForm, UserProfileUpdateForm
from apps.core.utils import log_action
from apps.bookings.models import Booking

def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    next_url = request.GET.get('next', 'accounts:dashboard')
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            customer_role = Role.objects.filter(code='CUSTOMER').first()
            if customer_role:
                user.role = customer_role
            user.loyalty_points = 100 # Welcome bonus
            user.save()
            
            # Record welcome bonus
            LoyaltyPointsLedger.objects.create(
                user=user,
                points_change=100,
                balance_after=100,
                transaction_type='EARN',
                reason='🎉 Welcome Bonus Points'
            )
            
            log_action(user, 'CREATE', 'User', user.id, f"New customer registration: {user.username}")
            login(request, user)
            messages.success(request, f"Welcome to Gammers Adda, {user.gamer_tag or user.username}! You've been awarded 100 Welcome XP Points!")
            return redirect(next_url)
    else:
        form = CustomerRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form, 'next': next_url})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    next_url = request.GET.get('next')
    if request.method == 'POST':
        form = CustomerLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            log_action(user, 'LOGIN', 'User', user.id, f"User logged in: {user.username}")
            messages.success(request, f"Welcome back, {user.gamer_tag or user.username}!")
            
            if next_url:
                return redirect(next_url)
            
            # Smart redirect based on role
            if user.is_superuser or (user.role and user.role.code in ['ADMIN', 'SUPER_ADMIN']):
                return redirect('dashboard:admin_dashboard')
            elif user.role and user.role.code in ['STAFF', 'MANAGER']:
                return redirect('staff:live_arena')
            return redirect('accounts:dashboard')
    else:
        form = CustomerLoginForm()
    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    if request.user.is_authenticated:
        log_action(request.user, 'LOGOUT', 'User', request.user.id, "User logged out")
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('core:home')


@login_required
def dashboard_view(request):
    user = request.user
    upcoming_bookings = Booking.objects.filter(
        user=user,
        status__in=['CONFIRMED', 'SEAT_HELD', 'CHECKED_IN', 'IN_SESSION']
    ).order_by('booking_date', 'start_time')
    
    past_bookings = Booking.objects.filter(
        user=user,
        status__in=['COMPLETED', 'CANCELLED', 'REFUNDED', 'NO_SHOW']
    ).order_by('-booking_date', '-start_time')[:10]
    
    recent_points = user.points_ledger.all()[:5]
    
    # Calculate gamer tier
    total_hours = sum([b.duration_hours for b in user.bookings.filter(status='COMPLETED')])
    if total_hours >= 50:
        tier_name = 'Diamond Gamer'
        tier_badge = '💎 Diamond'
    elif total_hours >= 25:
        tier_name = 'Platinum Gamer'
        tier_badge = '🏆 Platinum'
    elif total_hours >= 10:
        tier_name = 'Gold Gamer'
        tier_badge = '🥇 Gold'
    elif total_hours >= 3:
        tier_name = 'Silver Gamer'
        tier_badge = '🥈 Silver'
    else:
        tier_name = 'Rookie Gamer'
        tier_badge = '🥉 Bronze'

    context = {
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'recent_points': recent_points,
        'total_hours': total_hours,
        'tier_name': tier_name,
        'tier_badge': tier_badge,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            log_action(user, 'UPDATE', 'User', user.id, "User updated profile information")
            messages.success(request, "Profile updated successfully!")
            return redirect('accounts:profile')
    else:
        form = UserProfileUpdateForm(instance=user)
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def rewards_view(request):
    user = request.user
    ledger = user.points_ledger.all()
    referral_link = request.build_absolute_uri(f"/accounts/register/?ref={user.referral_code}")
    
    return render(request, 'accounts/rewards.html', {
        'ledger': ledger,
        'referral_link': referral_link,
    })


@login_required
def security_view(request):
    user = request.user
    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            log_action(user, 'UPDATE', 'User', user.id, "User changed password")
            messages.success(request, "Your password was successfully updated!")
            return redirect('accounts:security')
    else:
        form = PasswordChangeForm(user)
    return render(request, 'accounts/security.html', {'form': form})
