from django.urls import path
from .views import(
    signup_view,
    login_view,
    verify_email,
    profile_view,
    forgot_password_view,
    reset_password_view,
)

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('verify-email/<uidb64>/<token>/', verify_email, name='verify_email'),
    path('profile/', profile_view, name='profile'),
    path('forgot/', forgot_password_view, name='forgot'),
    path('reset-password/<uidb64>/<token>/', reset_password_view, name='reset_password'),
]   
