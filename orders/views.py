from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from Authentication.permissions import AdminUpdateOnly
from .models import Orders
from products.models import Product
from .serializers import OrderSerializer
from .tasks import mail_order_status
from django.db import transaction
from products.models import Product
import json

class OrdersView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [AdminUpdateOnly]

    def get(self, request):
        if not request.user.is_staff:
            orders = Orders.objects.filter(user=request.user)

        else:
            orders = Orders.objects.filter(store=request.user)
        
        serializer = OrderSerializer(orders, many=True)
        response = {
            'data': serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)

        
    def post(self, request):
        with transaction.atomic():
            data = json.loads(request.body)
            user = request.user
            product = Product.objects.get(id=data.get('product_id'))
            amount = product.price
            store = product.created_by
            quantity = data.get('quantity')

            Orders.objects.create(
                user=user,
                store=store,
                product=product,
                order_amount=amount,
                quantity=quantity
            )

        response = {
            'message': 'Order created successfully'
        }

        return Response(response, status=status.HTTP_201_CREATED)

    def delete(self, request):
        data = json.loads(request.body)
        order_id = data.get('order_id')
        order = Orders.objects.filter(user=request.user, order_id=order_id)
        if order.exists():
            order.delete()
            response = {
                'message': 'Order deleted'
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response({'error': 'No such order exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        data = json.loads(request.body)
        order_id = data.get('order_id')
        order_status = data.get('order_status').lower()
        order = Orders.objects.filter(store=request.user, order_id=order_id)
        if order.exists():
            order = order.first()
            match order_status:
                case 'pending':
                    order.order_status = Orders.OrderStatus.PENDING
                case 'paid':
                    order.order_status = Orders.OrderStatus.PAID
                    order.product.available_units -= 1
                    order.product.sold_units += 1
                    order.product.save()
                case 'processing':
                    order.order_status = Orders.OrderStatus.PROCESSING
                case 'shipped':
                    order.order_status = Orders.OrderStatus.SHIPPED
                case 'delivered':
                    order.order_status = Orders.OrderStatus.DELIVERED
                case 'cancelled':
                    order.order_status = Orders.OrderStatus.CANCELLED
                case _:
                    return Response({'error': 'Invalid status choice'}, status=status.HTTP_400_BAD_REQUEST)

            order.save()
            mail_order_status.delay(order.order_id, order_status, order.user.email)
            return Response({'message': 'Order status updated'}, status=status.HTTP_202_ACCEPTED)
        
        return Response({'error': 'No such order exists'}, status=status.HTTP_400_BAD_REQUEST)
