from django.shortcuts import render, redirect
from django.http import JsonResponse

from .models import Cart
from products.models import Product
from orders.models import Order
from accounts.forms import LoginForm, GuestForm
from accounts.models import GuestEmail
from billing.models import BillingProfile
from addresses.forms import AddressForm
from addresses.models import Address

def cart_detail_api_view(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    products = [{'id':product.id, 'name': product.title, 'price': product.price, 'url': product.get_absolute_url()} for product in cart_obj.products.all()]
    json_data = {
        'products': products,
        'subtotal': cart_obj.subtotal,
        'total': cart_obj.total,
    }
    return JsonResponse(json_data)

def cart_home(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    return render(request, 'carts/home.html', {'cart': cart_obj})

def cart_update(request):
    product_id = request.POST.get('product_id')
    if product_id is not None:
        try:
            product_obj = Product.objects.get(id = product_id)
        except Product.DoesNotExist:
            print('Show message to user, product is gone!')
            return redirect('carts:cart_home')
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        if product_obj in cart_obj.products.all():
            cart_obj.products.remove(product_obj)
            added = False
        else:
            cart_obj.products.add(product_obj)
            added = True
            # cart_obj.products.add(product_id)
        request.session['cart_items'] = cart_obj.products.count()
        if request.is_ajax():
            print('Ajax request')
            json_data = {
                'added': added,
                'removed': not added,
                'cartItemCount': cart_obj.products.count(),
            }
            return JsonResponse(json_data)
            # return JsonResponse({'message': 'Error'}, status = 400)
    return redirect('carts:cart_home')

def checkout_home(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    if new_obj or cart_obj.products.count() == 0:
        return redirect('carts:cart_home')
    # else:
    #     order_obj, new_order_obj = Order.objects.get_or_create(cart = cart_obj)

    order_obj = None
    address_qs = None
    login_form = LoginForm()
    guest_form = GuestForm()
    address_form = AddressForm()
    billing_address_id = request.session.get('billing_address_id', None)
    shipping_address_id = request.session.get('shipping_address_id', None)
    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)

    if billing_profile is not None:
        if request.user.is_authenticated:
            address_qs = Address.objects.filter(billing_profile = billing_profile)

        order_obj, order_obj_created = Order.objects.new_or_get(billing_profile = billing_profile, cart_obj = cart_obj)
        if shipping_address_id:
            order_obj.shipping_address = Address.objects.get(id = shipping_address_id)
            del request.session['shipping_address_id']
        if billing_address_id:
            order_obj.billing_address = Address.objects.get(id = billing_address_id)
            del request.session['billing_address_id']
        if billing_address_id or shipping_address_id:
            order_obj.save()

    if request.method == 'POST':
        is_done = order_obj.check_done()
        if is_done:
            order_obj.mark_paid()
            request.session['cart_items'] = 0
            del request.session['cart_id']
            return redirect('carts:success')

    context = {
        'order': order_obj,
        'billing_profile': billing_profile,
        'login_form': login_form,
        'guest_form': guest_form,
        'address_form': address_form,
        'address_qs': address_qs,
    }
    return render(request, 'carts/checkout.html', context)

def checkout_done(request):
    return render(request, 'carts/checkout_done.html', {})