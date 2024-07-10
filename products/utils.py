from rest_framework.response import Response
from rest_framework import status
from .models import Product
import base64, io, redis
from PIL import Image
from django.contrib.auth.models import User

r = redis.Redis(host="localhost", port=6379)

def action_handler(data, user_id, product=None):
    user = User.objects.get(id=user_id)
    sku = data.get('sku')
    if not sku:
        return Response({'error': 'Invalid SKU'}, status=status.HTTP_400_BAD_REQUEST)
    
    if Product.objects.filter(sku=sku).exists() and not product:
        return Response({'error': 'SKU already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    if len(sku) > 100:
        return Response({'error': 'SKU cannot be more than 100 characters'}, status=status.HTTP_400_BAD_REQUEST)
    
    name = data.get('name')
    descp = data.get('description')
    price = data.get('price')
    if not isinstance(price, float):
        return Response({'error': 'Price must be a number'}, status=status.HTTP_400_BAD_REQUEST)

    image = data.get('image')
    if image:
        image_bytes = base64.b64decode(image)
        image_data = Image.open(io.BytesIO(image_bytes))
        if image_data.format.lower() not in ("jpg", "jpeg", "png"):
            return Response({'error': 'Image format not supported.'}, status=status.HTTP_400_BAD_REQUEST)
        image_data.save('media/product_images/'+sku+'.jpg')
        
    slug = data.get('slug')
    if Product.objects.filter(slug=slug).exists() and not product:
        return Response({'error': 'Slug already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    available_units = data.get('available_units')
    if not isinstance(available_units, int):
        return Response({'error': 'Available units must be a number'}, status=status.HTTP_400_BAD_REQUEST)
    
    if product:
        product.sku = sku
        product.name = name
        product.description = descp
        product.price = price
        product.image = image
        product.slug = slug
        product.available_units = available_units
        product.save()
        r.set(f'no_stock_{product.id}', 0)
        r.set(f'low_stock_{product.id}', 0)

        response = {
        'message' : 'Product updated successfully'
        }
        return Response(response, status=status.HTTP_201_CREATED)

    product = Product.objects.create(
                sku = sku,
                name = name,
                description = descp,
                price = price,
                image = image, 
                slug = slug,
                available_units = available_units,
                created_by = user
            )
    response = {
    'message' : 'Product created successfully'
    }
    r.set(f'no_stock_{product.id}', 0)
    r.set(f'low_stock_{product.id}', 0)
    return Response(response, status=status.HTTP_201_CREATED)
