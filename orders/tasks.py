from celery import shared_task
from django.core.mail import send_mail
import os

@shared_task
def mail_order_status(order_id, order_status, receiver):
    subject = 'Status of your has changed'
    message = f'Dear Customer, the status of your order {order_id} has changed to {order_status}'
    from_email = os.getenv('DEFAULT_FROM_EMAIL')
    recipient_list = [receiver]

    send_mail(subject, message, from_email, recipient_list)
    return "Order status email sent"