from celery import shared_task
import time

@shared_task
def generate_invoice(order_id):
    time.sleep(3) # Simulating complex PDF generation
    return f"PDF Invoice generated for Order #{order_id}"

@shared_task
def send_confirmation_email(order_id):
    time.sleep(2) # Simulating SMTP network latency
    return f"Email sent to customer for Order #{order_id}"

@shared_task
def notify_warehouse(order_id):
    time.sleep(1) # Simulating external API payload
    return f"Warehouse alerted for Order #{order_id}"