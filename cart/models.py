from django.db import models
from django.contrib.auth.models import User
from products.models import Product

class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created_on = models.DateTimeField(auto_now_add=True)
