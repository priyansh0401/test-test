from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserProfileView, PasswordResetRequestView, PasswordResetConfirmView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', RegisterView.as_view(), name='auth_register'),
    path('me/', UserProfileView.as_view(), name='user_profile'),
    path('forgot-password/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('reset-password/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
