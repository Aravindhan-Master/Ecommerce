from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductsView.as_view(), name='products'),
    path('<str:slug>', views.ProductDetailsView.as_view(), name='details'),
]