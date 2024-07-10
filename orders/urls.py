from django.urls import path
from . import views

urlpatterns = [
    path('', views.OrdersView.as_view(), name='orders'),
]