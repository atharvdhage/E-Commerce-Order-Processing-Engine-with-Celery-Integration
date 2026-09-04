from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from cart.models import Cart
from .models import Order, OrderItem
from .tasks import process_professional_order, notify_warehouse

def checkout(request):
    if not request.user.is_authenticated:
        messages.error(request, "Please log in to checkout.")
        return redirect('/admin/login/?next=/cart/')

    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('/')

    # The Atomic Transaction Block
    try:
        with transaction.atomic():
            # 1. Create the master Order record (defaults to PENDING state)
            order = Order.objects.create(user=request.user, status='PENDING')

            # 2. Convert CartItems to OrderItems and take the price snapshot
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price_at_purchase=item.product.price, # The historical snapshot!
                    quantity=item.quantity
                )

            # 3. Empty the cart since the order is placed
            cart_items.delete()

        messages.success(request, f"Order #{order.id} placed successfully! Status is {order.get_status_display()}.")
        return redirect(f'/orders/{order.id}/')

    except Exception as e:
        messages.error(request, "An error occurred during checkout. Please try again.")
        return redirect('/cart/')

# A simple view to display the final receipt
def order_detail(request, order_id):
    if not request.user.is_authenticated:
        return redirect('/admin/login/')
        
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

def process_payment(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        if order.status == 'PENDING':
            order.status = 'SUCCESS'
            order.save() # The transaction is locked in
            
            # V3: Fire off the background tasks
            process_professional_order.delay(order.id)
            notify_warehouse.delay(order.id)

            messages.success(request, f"Payment for Order #{order.id} was successful!")
            
        return redirect(f'/orders/{order.id}/')
    return redirect('/')