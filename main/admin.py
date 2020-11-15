from django.contrib import admin
from .models import Profile, Transaction, UserNotification,  PaymentDate
# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'refered_by', 'account_status', 'balance']
    


class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id','user','transaction_type','created']

class UserEarningAdmin(admin.ModelAdmin):
    list_display = ['id','user','person_refered','amount']  

admin.site.register(Profile, ProfileAdmin)  
admin.site.register(Transaction, TransactionAdmin)           
admin.site.register(PaymentDate)