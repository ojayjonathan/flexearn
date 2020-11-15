from django.urls import path
from .views import (index, dashboard,loginView, changePassword, 
              register, email_confirmation, logoutView, setNewPassword,
              invite,activate_account, resend_account_confirmation)

urlpatterns = [
    path('', index, name="index"),
    path('dashboard/', dashboard, name="dashboard"),
    path("login/",loginView,name="login"),
    path("register/",register,name="register"),
    path("reset-password/",changePassword,name="reset_p"),
    path("email-confirmation/",email_confirmation,name="email_confirmation"),
    path("logout/",logoutView ,name="logout"),
    path("invite/<str:q>",invite,name="invite"),
    path("activate/<uidb64>/<token>/",activate_account,name="activate"),
    path("resend-confirmation/",resend_account_confirmation),
    path("set-new-password/<uidb64>/<token>",setNewPassword,name='set-new-password')
 
]
