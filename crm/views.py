from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Customer, PaymentReminder

@login_required
def CustomerList(request):
    customers = Customer.objects.all().order_by('-created_at')
    return render(request, 'crm/customer_list.html', {'customers': customers})

@login_required
def CustomerAdd(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()
        outstanding_balance = request.POST.get('outstanding_balance', '0').strip()

        if not name or not phone:
            messages.warning(request, 'Name and Phone are required!')
            return redirect('CustomerAdd')

        try:
            balance = float(outstanding_balance) if outstanding_balance else 0.00
        except ValueError:
            balance = 0.00

        Customer.objects.create(
            name=name,
            phone=phone,
            email=email if email else None,
            address=address if address else None,
            outstanding_balance=balance
        )
        messages.success(request, f'Customer "{name}" added successfully!')
        return redirect('CustomerList')

    return render(request, 'crm/customer_add.html')

@login_required
def CustomerEdit(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        customer.name = request.POST.get('name', customer.name).strip()
        customer.phone = request.POST.get('phone', customer.phone).strip()
        customer.email = request.POST.get('email', '').strip() or None
        customer.address = request.POST.get('address', '').strip() or None
        outstanding = request.POST.get('outstanding_balance', '0').strip()
        try:
            customer.outstanding_balance = float(outstanding)
        except ValueError:
            customer.outstanding_balance = 0.00
        customer.save()
        messages.success(request, f'Customer "{customer.name}" updated successfully!')
        return redirect('CustomerList')

    return render(request, 'crm/customer_edit.html', {'customer': customer})

@login_required
def CustomerDelete(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    name = customer.name
    customer.delete()
    messages.success(request, f'Customer "{name}" deleted successfully!')
    return redirect('CustomerList')

import urllib.parse
# TIP: For automatic SMS, you can integrate services like Twilio or Fast2SMS here.
# from your_sms_provider import send_sms 

@login_required
def SendReminder(request, customer_id):
    """
    Developer Note: This view handles payment reminders. 
    Currently using WhatsApp redirection (Free & No Setup).
    To switch to Automatic SMS, integrate an API like Twilio/Fast2SMS.
    """
    customer = get_object_or_404(Customer, id=customer_id)
    
    # 1. Prepare Message
    message = (
        f"Dear {customer.name}, this is a reminder from JCB Parts Inventory. "
        f"You have a pending balance of ₹{customer.outstanding_balance}. "
        "Please clear it at your convenience. Thank you!"
    )
    
    # 2. Log the reminder in Database
    PaymentReminder.objects.create(
        customer=customer,
        message=message
    )
    
    # 3. Handle Delivery (WhatsApp Method)
    # Format phone: remove non-digits and add India code if missing
    phone = "".join(filter(str.isdigit, customer.phone))
    if len(phone) == 10:
        phone = "91" + phone
        
    # --- AUTOMATIC SMS GATEWAY (PLACEHOLDER) ---
    # if API_KEY_AVAILABLE:
    #     send_sms(phone, message)
    #     messages.success(request, f"Automatic SMS sent to {customer.name}!")
    #     return redirect('CustomerList')
    # --------------------------------------------

    # Fallback to WhatsApp Redirection
    encoded_msg = urllib.parse.quote(message)
    whatsapp_url = f"https://api.whatsapp.com/send?phone={phone}&text={encoded_msg}"
    
    messages.success(request, f"Opening WhatsApp to send reminder to {customer.name}...")
    return redirect(whatsapp_url)
