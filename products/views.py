from django.shortcuts import get_object_or_404
from django.core import paginator
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer
from Authentication.serializers import UserSerializer
from .tasks import bulk_upload
from .utils import action_handler
from Authentication.permissions import IsAdminOrReadOnly
import json

PRODUCT_IMAGE_PATH = 'media/products/uploads'

class ProductsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        products = Product.objects.all()
        if 'search' in request.GET:
            search_value = request.GET.get('search')
            products = products.filter(name__icontains=search_value)

        if 'filter' in request.GET:   # filter particular store's products
            products = products.filter(created_by=request.user)

        if 'sort' in request.GET:     # sort by price
            products = products.order_by('price')

        products_list = paginator.Paginator(products, 10)
        page_num = request.GET.get('page') 
        products_data = products_list.get_page(page_num)
        serializer = ProductSerializer(products_data.object_list, many=True)

        response = {
            'data': serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)

    def post(self, request):
        data = json.loads(request.body)
        if 'products' in data:  # bulk upload
            task = bulk_upload.delay(data['products'], request.user.id)
            response = {
                'message': f'Bulk upload started. Here is the task is {task.id}',
            }
            return Response(response, status=status.HTTP_202_ACCEPTED)
        response = action_handler(data, user_id=request.user.id)
        return response

class ProductDetailsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        serializer = ProductSerializer(product)
        response = {
            'data': serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)
    
    def put(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        response = action_handler(request.body, product)
        return response
    
    def delete(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        product.delete()
        response = {
            'message': 'Product deleted successfully'
        }
        return Response(response, status=status.HTTP_200_OK)