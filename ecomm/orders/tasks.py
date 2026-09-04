import io
import time
from celery import shared_task
from django.core.mail import EmailMessage
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from .models import Order

@shared_task
def process_professional_order(order_id):
    order = Order.objects.get(id=order_id)
    
    # 1. Draw Professional PDF in RAM
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Header
    p.setFont("Helvetica-Bold", 24)
    p.drawString(50, 750, "OFFICIAL INVOICE")
    p.setFont("Helvetica", 12)
    p.drawString(50, 720, f"Order Number: #{order.id}")
    p.drawString(50, 700, f"Date: {order.created_at.strftime('%B %d, %Y')}")
    p.drawString(50, 680, f"Customer: {order.user.username}")
    
    # Table Headers
    p.line(50, 650, 550, 650)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 630, "Product")
    p.drawString(350, 630, "Qty")
    p.drawString(450, 630, "Price")
    p.line(50, 615, 550, 615)
    
    # Itemized List
    y = 590
    total = 0
    p.setFont("Helvetica", 12)
    for item in order.items.all():
        p.drawString(50, y, item.product.name)
        p.drawString(350, y, str(item.quantity))
        line_total = item.price_at_purchase * item.quantity
        p.drawString(450, y, f"${line_total:.2f}")
        total += line_total
        y -= 25
        
    # Total Calculation
    p.line(50, y, 550, y)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(350, y - 25, "TOTAL:")
    p.drawString(450, y - 25, f"${total:.2f}")
    
    p.save()
    buffer.seek(0)
    
    # 2. Attach and Send Real Email
    email = EmailMessage(
        subject=f'Your Invoice - Order #{order.id}',
        body=f'Thank you for your purchase, {order.user.username}!\n\nYour order has been confirmed. Please find your professional PDF invoice attached.',
        from_email=None, # Automatically uses EMAIL_HOST_USER from settings
        to=[order.user.email],
    )
    email.attach(f'invoice_{order.id}.pdf', buffer.read(), 'application/pdf')
    email.send(fail_silently=False)
    
    return f"Invoice generated and emailed to {order.user.email}"

@shared_task
def notify_warehouse(order_id):
    # Simulate a slow network request to a 3rd-party inventory system
    time.sleep(3) 
    return f"Warehouse alerted to pack Order #{order_id}"