from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re
from django.db.models import Q

email_re = r"\w+\@\w+\.\w+"
phone_re1 = r"01\w{8}"
phone_re2 = r"07\w{8}"


User = get_user_model()


class UserCreationForm(forms.Form):
    password1 = forms.CharField(max_length=50)
    password2 = forms.CharField(max_length=50)
    phone_number = forms.CharField(max_length=12)
    username = forms.CharField(max_length=50)
    email = forms.CharField(max_length=50)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number or len(phone_number) != 10:
            raise ValidationError("Invalid Phone number ")
        if phone_number and re.match(phone_re1, phone_number) or re.match(phone_re2, phone_number):
            return phone_number
        raise ValidationError("Invalid Phone number ")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        r = User.objects.filter(email=email)
        if r.count():
            raise ValidationError("User exist please login")
        if email and re.match(r"\w+\@\w+\.\w+", email):
            return email
        raise ValidationError('Invalid email')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        r = User.objects.filter(username=username)
        if r.count():
            raise ValidationError("Username already in use")

        return username

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password and len(password) < 6 or len(password) > 50:
            raise ValidationError("password must be between 6-50 characters")
        return password

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if not (password1 == password2):
            raise ValidationError("Passwords didn't match")
        return password2

    def save(self, commit=False):
        user = User.objects.create_user(
            username=self.cleaned_data.get('username'),
            email=self.cleaned_data.get('email'),


        )
        return user



class PasswordResetForm(forms.Form):
    password = forms.CharField(max_length=18)
    password1 = forms.CharField(max_length=18)
    help_text = 'password should have atleast 6 characters'

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password and len(password) < 6 or len(password) > 50:
            raise ValidationError("password must be between 6-50 characters")
        return password

    def clean_password1(self):
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password1')
        if not (password1 == password2):
            raise ValidationError("Passwords didn't match")
        return password2


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(max_length=50)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        r = User.objects.filter(Q(username=username) | Q(email=username))
        if not r.count():
            raise ValidationError("Invalid Email or Username")
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password is None:
            raise ValidationError("Invalid Email or Username")
        return password


# class ChangeUsernameForm(forms.Form):
#     username = forms.CharField(max_length=50)

#     def clean_username(self):
#         username = self.cleaned_data['username']
#         r = User.objects.filter(username=username)
#         if r.count():
#             raise ValidationError(
#                 [ValidationError(_('You can not change your Email or Phone Number to the current one '), 'error'),
#                  ValidationError(_('Email or Phone Number is in use '), code='error')])
#         if re.match(email_re, username) or re.match(phone_re1, username) or re.match(phone_re2, username):
#             return username
#         raise ValidationError([
#             ValidationError(
#                 _('You can not change your Email or Phone Number to the current one '), code='error'),
#             ValidationError(_('Email or Phone Number provided is invalid'), code='error2')])


# class ResetPasswordForm(forms.Form):
#     username = forms.CharField(max_length=50)
#     new_password = forms.CharField(max_length=50)

#     def clean_username(self):
#         username = self.cleaned_data['username']
#         r = User.objects.filter(username=username)
#         if not r.count():
#             raise ValidationError(
#                 _("User Doesn't exists"), code='invalid user')
#         return username

#     def clean_password(self):
#         password = self.cleaned_data['new_password')
#         return password
