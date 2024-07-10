from django.db import models
from django.contrib.auth.models import User
from products.models import Product
import uuid

class Orders(models.Model):
    class OrderStatus(models.IntegerChoices):
        PENDING = 1, "Pending"
        PAID = 2, "Paid"
        PROCESSING = 3, "Processing"
        SHIPPED = 4, "Shipped"
        DELIVERED = 5, "Delivered"
        CANCELLED = 0, "Cancelled"

    order_id = models.UUIDField(default=uuid.uuid4().__str__())
    store = models.ForeignKey(User, on_delete=models.CASCADE, related_name='store')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.IntegerField(choices=OrderStatus.choices, default=OrderStatus.PENDING)
    order_amount = models.FloatField(default=0.0)

