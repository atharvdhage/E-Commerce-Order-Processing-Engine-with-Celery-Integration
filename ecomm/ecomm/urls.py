"""
URL configuration for ecomm project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from catalog import views as catalog_views
from cart import views as cart_views
from orders import views as order_views

# username=dhage
# pass=TRUPTIDR
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', catalog_views.product_list, name='product_list'), 
    path('cart/', cart_views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', cart_views.add_to_cart, name='add_to_cart'),
    # NEW: The path to remove an item
    path('cart/remove/<int:item_id>/', cart_views.remove_from_cart, name='remove_from_cart'),
    #new path for v2
    path('checkout/', order_views.checkout, name='checkout'),
    path('orders/<int:order_id>/', order_views.order_detail, name='order_detail'),
    #payment path
    path('orders/<int:order_id>/pay/', order_views.process_payment, name='process_payment'),
]