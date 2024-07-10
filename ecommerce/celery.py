import os
from celery import Celery
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce.settings")
app = Celery("ecommerce")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "every_1_minute": {
        "task": "products.tasks.remind_low_stock",
        "schedule":datetime.timedelta(minutes=1),
    },
}