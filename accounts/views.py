from django.shortcuts import render
from .forms import CustomUserCreationForm
from .utils import send_verification_email, send_password_reset_email
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_verification_email(request, user)
            return redirect("login")
            #test verification
            # verification_link = test_verification_email(request, user)
            # return render(request, "accounts/emailVerificationEmail.html", {"verification_link": verification_link}) 
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/signup.html", {"form": form})


def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        User = get_user_model()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_verified = True
        user.save()
        messages.success(request, 'Your email has been verified. You can now log in.')
        return redirect('login')
    else:
        messages.error(request, 'Verification link is invalid or has expired.')
        return redirect('signup')


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("profile")
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, "accounts/login.html")

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")



def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            send_password_reset_email(request, user)
            messages.success(request, "Password reset email has been sent.")
            #test password reset
            # password_reset_link = test_password_reset_email(request, user)
            # return render(request, "accounts/passwordResetEmail.html", {"password_reset_link": password_reset_link})
            return redirect("login")
        except User.DoesNotExist:
            messages.error(request, "Email not found.")
    return render(request, "accounts/forgot.html")



def reset_password_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        User = get_user_model()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            if new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, "accounts/resetPassword.html")
            user.set_password(new_password)
            user.save()
            messages.success(request, "Your password has been reset successfully.")
            return redirect("login")
        return render(request, "accounts/resetPassword.html")
    else:
        messages.error(request, "Password reset link is invalid or has expired.")
        return redirect("login")
    

@login_required
def profile_view(request):
    user = request.user
    if request.method == "POST":
        user.email = request.POST.get("email", user.email)
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.address = request.POST.get("address", user.address)
        user.city = request.POST.get("city", user.city)
        user.postcode = request.POST.get("postcode", user.postcode)
        user.country = request.POST.get("country", user.country)
        user.mobile = request.POST.get("mobile", user.mobile)
        if request.FILES.get("profile_picture"):
            user.profile_picture = request.FILES.get("profile_picture")
        user.save()
        messages.success(request, "Profile updated successfully.")
    return render(request, "accounts/profile.html", {"user": user})


@login_required
def change_password_view(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return render(request, "accounts/changePassword.html")

        user = authenticate(request, email=request.user.email, password=current_password)
        if user is not None:
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password changed successfully.")
            return redirect("login")
        else:
            messages.error(request, "Current password is incorrect.")
    return render(request, "accounts/changePassword.html")