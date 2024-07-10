from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from Authentication.permissions import IsAdminOrReadOnly
from .models import ShoppingCart
from products.models import Product
from .serializers import CartSerializer
import json

class CartView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        carts = ShoppingCart.objects.filter(user=request.user)
        total_price = 0
        for cart in carts:
            total_price += cart.product.price
        serializer = CartSerializer(carts, many=True)

        response = {
            'data': serializer.data,
            'total_amount': total_price
        }
        return Response(response, status=status.HTTP_200_OK)

    def post(self, request):
        data = json.loads(request.body)
        product = Product.objects.get(id=data.get('product_id'))
        quantity = data.get('quantity')
        cart = ShoppingCart.objects.create(user=request.user, product=product, quantity=quantity)
        response = {
            'message': 'Product added to cart'
        }
        return Response(response, status=status.HTTP_201_CREATED)
    
    def delete(self, request):
        data = json.loads(request.body)
        product = Product.objects.get(id=data.get('product_id'))
        ShoppingCart.objects.get(user=request.user, product=product).delete()
        response = {
            'message': 'Product removed from cart'
        }
        return Response(response, status=status.HTTP_200_OK)
    
    def put(self, request):
        data = json.loads(request.body)
        product = Product.objects.get(id=data.get('product_id'))
        quantity = data.get('quantity')
        cart = ShoppingCart.objects.get(user=request.user, product=product)
        cart.quantity = quantity
        cart.save()

        response = {
            'message': 'Cart updated'
        }
        return Response(response, status=status.HTTP_200_OK)
