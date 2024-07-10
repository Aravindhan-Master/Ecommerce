from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    sku = models.CharField(max_length=100, null=False, unique=True)
    name = models.CharField(max_length=256)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.CharField(max_length=256, blank=True, null=True)
    slug = models.SlugField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    available_units = models.BigIntegerField()
    sold_units = models.BigIntegerField(default=0)