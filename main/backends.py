# Django
from django.contrib.auth.backends import ModelBackend
# Models
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailUsernameModelBackend(ModelBackend):
    """
    authentication class to login with the email address or username.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if password is None:
            return None
        try:
            user = User.objects.get(Q(username=username) | Q(email=username))

        except User.DoesNotExist:
            User.set_password(password)

        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
