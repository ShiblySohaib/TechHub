from django.urls import path
from .views import(
    signup_view,
    login_view,
    verify_email,
    profile_view,
)

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('verify-email/<uidb64>/<token>/', verify_email, name='verify_email'),
    path('profile/', profile_view, name='profile'),
]   
