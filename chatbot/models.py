from django.db import models
from django.conf import settings
from store.models import Product, Category
from accounts.models import Account  # Custom user model

class ChatbotFeedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    query = models.TextField()
    feedback = models.CharField(max_length=10)  # e.g. 'Yes' or 'No'
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user} - {self.feedback}"
    
class CustomerBehavior(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    views = models.IntegerField(default=1)
    last_viewed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.product.product_name} views: {self.views}"

class PurchaseHistory(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    purchased_on = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=1)

    # For chatbot personalization
    last_searched = models.DateTimeField(auto_now=True)
    purchase_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.email} - {self.product.product_name} x {self.quantity}"

