from django.shortcuts import render
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import UserCreationForm, LoginForm, PasswordResetForm
from .models import Profile, UserNotification,  PaymentDate
import string
import secrets
import datetime
from django.core.mail import send_mail
from django.conf import settings
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .token_generator import account_activation_token

User = get_user_model()


def random_token():
    a = string.ascii_letters + string.digits
    return ''.join(secrets.choice(a) for i in range(10))


def index(request):

    return render(request, 'index.html')


@login_required
def dashboard(request):
    profile = Profile.objects.filter(user=request.user).first()
    notifications = UserNotification.objects.filter(user=request.user)
    date = PaymentDate.objects.first()
    next_payment = datetime.datetime(
        date.date.year, date.date.month, date.date.day, date.date.hour)
    time_delta = next_payment - datetime.datetime.now()
    distance_in_seconds = time_delta.days*24*60*60+time_delta.seconds
    count_down = {
        "hours": int(distance_in_seconds / (60 * 60)),
        "minutes": int((distance_in_seconds % (60 * 60)) / (60)),
        "seconds": int((distance_in_seconds % (60)))
    }

    return render(request, 'dashboard.html', {
        'profile': profile,
        'notifications': notifications,
        'count_down': count_down
    })


def logoutView(request):
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect(reverse('login'))


def loginView(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('dashboard'))
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('dashboard'))
        return render(request, 'login.html',
                      {'form': login_form, 'errors': 'Invalid Credentials'})
    return render(request, 'login.html')


def register(request):
    if request.user.is_authenticated:
        HttpResponseRedirect(reverse('dashboard'))
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password1'))
            user.is_active = False
            user.save()
            profile = Profile(
                user=user,
                invite_link=random_token(),
                phone_number=form.cleaned_data.get('phone_number'),

            )
            notification = UserNotification(
                user=user,
                text="Your account was created successfully",
                notification_type='Registration',
            ).save()

            if request.session.get('INVITED_BY'):
                invited_by = Profile.objects.filter(
                    invite_link=request.session.get('INVITED_BY')).first()
                if invited_by is not None and invited_by.user is not profile.user:
                    profile.refered_by = invited_by.user
                    UserNotification(
                        user=invited_by.user,
                        text=f"Your friend {profile.user.username[:3]}*** has joined, you will earn when they activate their account",
                        notification_type='Friend join',
                    ).save()
            profile.save()
            subject = 'Flexearn Registration'
            message = render_to_string('activate_account.html', {
                'user': user,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            email_from = settings.EMAIL_HOST_USER
            user_email = form.cleaned_data.get('email')
            recipient_list = [user_email, ]
            send_mail(subject, message, email_from, recipient_list,
                      fail_silently=True, html_message=message)
            return HttpResponse(render(request, 'redirect.html', {'message':
                                                                  f"<span>Please follow the link send to  <a href='#'>\
                                                                  {user_email} </a> to confirm your account</span>",
                                                                  "title": 'Registration Confirmation'}))
        else:
            return render(request, 'register.html', {'form': form})
    return render(request, 'register.html')


def activate_account(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse(render(request, 'redirect.html', {'message':
                                                              "<span>Your email has been confirmed <a href='/login'>Login<a/></span>",
                                                              "title": 'Account activation'}))
    else:
        return HttpResponse(render(request, 'redirect.html', {'message':
                                                              "<span>Invalid confirmation link or it has expired <a href='/resend-confirmation/'>resend<a/></span>",
                                                              "title": 'Account Cofirmation'}))


def resend_account_confirmation(request):
    errors = None
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user is not None:
            subject = 'Account confirmation code'
            message = render_to_string('activate_account.html', {
                'user': user,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            email_from = settings.EMAIL_HOST_USER
            user_email = request.POST.get('email')
            recipient_list = [email, ]
            send_mail(subject, message, email_from, recipient_list,
                      fail_silently=True, html_message=message)
            return HttpResponse(render(request, 'redirect.html', {'message':
                                                                  f"<span>Please follow the link send to  <a href='#'>\
                                                                {email} </a> to confirm your account",
                                                                  'title': 'Confirmation code'}))
        errors = 'Invalid Email'
    return HttpResponse(render(request, 'resend.html', {
        "action": '/resend-confirmation/',
        "title": 'Enter your email to receive confirmation code',
        "errors": errors,
    }))


def changePassword(request):
    errors = None
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user is not None:
            subject = 'Change password'
            message = render_to_string('change_password_email.html', {
                'user': user,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            email_from = settings.EMAIL_HOST_USER
            user_email = request.POST.get('email')
            recipient_list = [email, ]
            send_mail(subject, message, email_from, recipient_list,
                      fail_silently=True, html_message=message)
            return HttpResponse(render(request, 'redirect.html', {'message':
                                                                  f"<span>Please follow the link send to  <a href='#'>\
                                                                {email} </a> reset your password",
                                                                  'title': 'Reset Password'}))

        else:
            errors = "Invalid email"
    return HttpResponse(render(request, 'resend.html', {
        "action": '/reset-password/',
        "title": 'Enter your email to change your password',
        "errors": errors
    }))


def setNewPassword(request, uidb64, token):
    form = None
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password1']
            try:
                uid = force_bytes(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None
            if user is not None and account_activation_token.check_token(user, token):
                user.set_password(password)
                user.save()
                return HttpResponse(render(request, 'redirect.html', {'message':
                                                                      "<span>Your password has been changed <a href='/login'>Login<a/></span>",
                                                                      "title": 'Set new password'}))
            else:
                return HttpResponse(render(request, 'redirect.html', {'message':
                                                                      "<span>The link has expired or is broken resend  <a href='/reset-password/'>\
                                                                 password</a> code",
                                                                      'title': 'Reset Password'}))
        return render(request, 'new_password.html', {'form': form})
    uid = force_bytes(urlsafe_base64_decode(uidb64))
    user = User.objects.filter(pk=uid).first()
    if user is not None and account_activation_token.check_token(user, token):
        return render(request, 'new_password.html', {'form': form})
    else:
        return HttpResponse(render(request, 'redirect.html', {'message':
                                                              "<span>The link has expired or is broken resend <a href='/reset-password/'>\
                                                                password reset </a> code",
                                                              'title': 'Reset Password'}))


def email_confirmation(request):
    return render(request, 'email_confirmation.html')


def invite(request, q):
    if request.user.is_authenticated:
        HttpResponseRedirect(reverse('dashboard'))
    request.session['INVITED_BY'] = q
    request.session.set_expiry(172800)
    return HttpResponseRedirect(reverse('register'))

def terms(request):
    return render(request, 'login.html')