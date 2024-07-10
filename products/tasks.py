from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from .utils import action_handler
from .models import Product
import redis, os

r = redis.Redis(host="localhost", port=6379)

@shared_task
def bulk_upload(products:list, user_id):
    for data in products:
        action_handler(data, user_id=user_id)
    
    return "Bulk upload completed"

@shared_task
def remind_low_stock():
    products = Product.objects.all()
    for product in products:
        if product.available_units == 0 and r.get(f'no_stock_{product.id}') != 1:
            subject = 'Out of stock'
            message = f'Dear Customer, your product {product.sku} went out of stock. Refill this as soon as possible.'
            from_email = os.getenv('DEFAULT_FROM_EMAIL')
            recipient_list = [product.created_by.email]

            send_mail(subject, message, from_email, recipient_list)

        elif product.available_units < 10 and r.get(f'low_stock_{product.id}') != 1:
            subject = 'Stock about to empty'
            message = f'Dear Customer, your product {product.sku} is about to empty. Refill this as soon as possible.'
            from_email = os.getenv('DEFAULT_FROM_EMAIL')
            recipient_list = [product.created_by.email]

            send_mail(subject, message, from_email, recipient_list)

    return "Stock reminder sent"