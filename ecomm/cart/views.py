from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from catalog.models import Product
from .models import Cart, CartItem

def cart_detail(request):
    if not request.user.is_authenticated:
        messages.error(request, "Please log in to view your cart.")
        return redirect('/admin/login/?next=/cart/')

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    return render(request, 'cart/cart_detail.html', {'cart_items': cart_items})

def add_to_cart(request, product_id):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to add items to your cart.")
            return redirect('/admin/login/?next=/')

        product = get_object_or_404(Product, id=product_id)
        requested_quantity = int(request.POST.get('quantity', 1))
        cart, _ = Cart.objects.get_or_create(user=request.user)

        if product.stock_quantity < requested_quantity:
            messages.error(request, f"Only {product.stock_quantity} units of {product.name} are available.")
            return redirect('/')

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            new_total_quantity = cart_item.quantity + requested_quantity
            if product.stock_quantity < requested_quantity: # Adjusted logic here
                messages.error(request, f"Not enough stock.")
                return redirect('/')
            cart_item.quantity = new_total_quantity
        else:
            cart_item.quantity = requested_quantity

        cart_item.save()

        # NEW: Deduct the stock from the main product database
        product.stock_quantity -= requested_quantity
        product.save()

        messages.success(request, f"Added {requested_quantity} of {product.name} to your cart.")
        return redirect('/cart/')
        
    return redirect('/')

# NEW: Function to handle removing items and restoring stock
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('/admin/login/?next=/cart/')
        
        # Ensure we only delete an item that belongs to the logged-in user's cart
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        product = cart_item.product
        
        # Restore the stock to the product database
        product.stock_quantity += cart_item.quantity
        product.save()
        
        # Delete the item from the cart
        cart_item.delete()
        messages.success(request, f"Removed {product.name} from your cart.")
        
    return redirect('/cart/')