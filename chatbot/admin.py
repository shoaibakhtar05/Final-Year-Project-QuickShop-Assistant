from django.contrib import admin

# Register your models here.
from .models import ChatbotFeedback
from django.contrib import admin
from .models import CustomerBehavior, PurchaseHistory  # <-- Make sure import ho

@admin.register(ChatbotFeedback)
class ChatbotFeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'feedback', 'timestamp']

admin.site.register(CustomerBehavior)
admin.site.register(PurchaseHistory)
