from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import (
    RegistrationForm, LoginForm, ResetPasswordEmailForm, SetNewPasswordForm,
    EditProfileForm, ChangePasswordForm
)
from django.contrib import messages
from .models import Account
from orders.models import Order
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from .models import UserProfile
from .forms import  UserProfileForm
# Register view
from django.contrib.auth import get_user_model

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')

                if not email or not password:
                    messages.error(request, "Email or password missing.")
                    return render(request, 'accounts/register.html', {'form': form})

                # Fallback for username
                user.username = email.split('@')[0] if email else "user" + str(User.objects.count())
                user.set_password(password)
                user.save()

                messages.success(request, "Registration successful.")
                return redirect('login')

            except Exception as e:
                print(f"Error in registration: {e}")
                messages.error(request, f"Error during registration: {e}")
        else:
            print("Form Errors:", form.errors)
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        user = None  # Initialize user before any conditional block

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(email=email, password=password)

            if user:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid credentials')
        else:
            print(form.errors)
            messages.error(request, 'Please correct the form errors.')

    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def dashboard(request):  
    try:
        userprofile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        userprofile = None  # or handle differently

    orders = Order.objects.filter(user=request.user)
    orders_count = orders.count()

    context = {
        'userprofile': userprofile,
        'orders_count': orders_count,
    }

    return render(request, 'accounts/dashboard.html', context)

# Forgot Password
def forgotPassword(request):
    if request.method == 'POST':
        form = ResetPasswordEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = Account.objects.filter(email=email).first()
            if user:
                mail_subject = 'Reset your password'
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_url = f"http://localhost:8000/accounts/reset_password_validate/{uid}/{token}/"
                message = render_to_string('accounts/reset_password_email.html', {
                    'user': user,
                    'reset_url': reset_url,
                })
                email_msg = EmailMessage(mail_subject, message, to=[email])
                email_msg.send()
                messages.success(request, 'Password reset email has been sent.')
            else:
                messages.error(request, 'Account not found.')
    else:
        form = ResetPasswordEmailForm()
    return render(request, 'accounts/forgotPassword.html', {'form': form})

# Reset Password Validate
def reset_password_validate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has expired.')
        return redirect('login')

# Reset Password Form
def resetPassword(request):
    if request.method == 'POST':
        form = SetNewPasswordForm(user=None, data=request.POST)
        if form.is_valid():
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            messages.success(request, 'Password reset successful.')
            return redirect('login')
    else:
        form = SetNewPasswordForm(user=None)
    return render(request, 'accounts/resetPassword.html', {'form': form})


#  My Orders
@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/my_orders.html', {'orders': orders})

#  Order Detail
@login_required(login_url='login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'accounts/order_detail.html', {'order': order})


@login_required(login_url='login')
def edit_profile(request):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)

    if request.method == 'POST':
        user_form = EditProfileForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('dashboard')
    else:
        user_form = EditProfileForm(instance=user)
        profile_form = UserProfileForm(instance=user_profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': user_profile,
    }
    return render(request, 'accounts/edit_profile.html', context)

#  Change Password
@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # keep user logged in
            messages.success(request, 'Password changed successfully.')
            return redirect('dashboard')
    else:
        form = ChangePasswordForm(user=request.user)
    return render(request, 'accounts/change_password.html', {'form': form})
