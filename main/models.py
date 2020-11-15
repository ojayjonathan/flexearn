from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

User = get_user_model()

TRANSACTION_TYPE_CHOICES = [
    ('D', 'Deposit'),
    ('W', 'widthdrawal'),

]
ACCOUNT_STATUS_CHOICES = [
    ('A', 'activated'),
    ('I', 'inactive'),

]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    refered_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="refered_by")
    invite_link = models.CharField(max_length=20,unique=True)
    account_status = models.CharField(
        max_length=1, choices=ACCOUNT_STATUS_CHOICES, default='I')
    profile_pic = models.ImageField(null=True, blank=True)
    phone_number = models.CharField(max_length=12)
    balance = models.IntegerField(default=0)

    def __str__(self):
        return str(self.user)

    def get_people_refered(self):
        return Profile.objects.filter(refered_by=self.user)    

    
class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    transaction_id = models.CharField(max_length=15)
    created = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(
        max_length=1, choices=TRANSACTION_TYPE_CHOICES)

class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.text
    @property
    def count(self):
        return self.user.usernotification_set.all().count()

      

class PaymentDate(models.Model):
    date = models.DateTimeField()    
    def __str__(self):
        return 'next_payment date'   