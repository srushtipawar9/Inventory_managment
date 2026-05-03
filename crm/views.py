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

@login_required
def SendReminder(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    # In a real app, this would send an SMS or Email
    # For now, we just create a record and show a success message
    PaymentReminder.objects.create(
        customer=customer,
        message=f"Reminder: Dear {customer.name}, you have a pending balance of ₹{customer.outstanding_balance}."
    )
    messages.success(request, f"Reminder sent to {customer.name}!")
    return redirect('CustomerList')
