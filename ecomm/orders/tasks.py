import time
from celery import shared_task
from django.core.mail import send_mail
from reportlab.pdfgen import canvas
from .models import Order

@shared_task
def generate_invoice(order_id):
    order = Order.objects.get(id=order_id)
    filename = f"invoice_order_{order.id}.pdf"
    
    # Generate a physical PDF document
    p = canvas.Canvas(filename)
    p.drawString(100, 800, f"OFFICIAL INVOICE")
    p.drawString(100, 780, f"Order ID: #{order.id}")
    p.drawString(100, 760, f"Customer: {order.user.username}")
    p.save()
    
    return f"Successfully generated {filename}"

@shared_task
def send_confirmation_email(order_id):
    order = Order.objects.get(id=order_id)
    
    # Send email (Routes to console based on your settings.py)
    send_mail(
        subject=f'Order #{order.id} Confirmed',
        message=f'Your order is now {order.status}. The warehouse is packing it.',
        from_email='sales@ecomm.com',
        recipient_list=[order.user.email],
        fail_silently=False,
    )
    return f"Confirmation email dispatched to {order.user.email}"

@shared_task
def notify_warehouse(order_id):
    # Simulate a slow network request to a 3rd-party inventory system
    time.sleep(3) 
    return f"Warehouse alerted to pack Order #{order_id}"