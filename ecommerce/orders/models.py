from django.db import models
from django.db.models.signals import pre_save, post_save
from django.urls import reverse
from django.conf import settings

from carts.models import Cart
from ecommerce.utils import unique_order_id_generator
from billing.models import BillingProfile
from addresses.models import Address
from products.models import Product

import math

User = settings.AUTH_USER_MODEL

ORDER_STATUS_CHOICES = (
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('shipped', 'Shipped'),
    ('refunded', 'Refunded'),
)

class OrderQuerySet(models.QuerySet):
    def by_billing_profile(self, request):
        billing_profile, created = BillingProfile.objects.new_or_get(request)
        return self.filter(billing_profile = billing_profile)

    def not_created(self):
        return self.exclude(status = 'created')

class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using = self._db)

    def by_billing_profile(self, request):
        return self.get_queryset().by_billing_profile(request)

    def new_or_get(self, billing_profile, cart_obj):
        created = False
        qs = self.get_queryset().filter(cart = cart_obj, billing_profile = billing_profile, active = True, status = 'created')
        if qs.count() == 1:
            obj = qs.first()
        else:
            obj = self.model.objects.create(cart = cart_obj, billing_profile = billing_profile)
            created = True
        return obj, created

# Create your models here.
class Order(models.Model):
    order_id = models.CharField(max_length = 120, blank = True)
    billing_profile = models.ForeignKey(BillingProfile, null = True, blank = True, on_delete = models.CASCADE)
    shipping_address = models.ForeignKey(Address, related_name = 'shipping_addresses', null = True, blank = True, on_delete = models.CASCADE)
    billing_address = models.ForeignKey(Address, related_name = 'billing_addresses', null = True, blank = True, on_delete = models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete = models.CASCADE)
    status = models.CharField(max_length = 120, default = 'created', choices = ORDER_STATUS_CHOICES)
    shipping_total = models.DecimalField(default = 2.99, max_digits = 20, decimal_places = 2)
    total = models.DecimalField(default = 0.00, max_digits = 20, decimal_places = 2)
    active = models.BooleanField(default = True)
    timestamp = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    objects = OrderManager()

    class Meta:
        ordering = ['-timestamp', '-updated']

    def __str__(self):
        return self.order_id

    def get_absolute_url(self):
        return reverse('orders:single-order', kwargs={'order_id': self.order_id})

    def get_shipping_status(self):
        if self.status == 'refunded':
            return 'Returned'
        elif self.status == 'shipped':
            return 'Shipped'
        return 'Shipping Soon'

    def update_total(self):
        cart_total = self.cart.total
        shipping_total = self.shipping_total
        new_total = math.fsum([cart_total, shipping_total])
        formatted_total = format(new_total, '.2f')
        self.total = formatted_total
        self.save()
        return new_total

    def check_done(self):
        shipping_address_required = not self.cart.is_digital
        if shipping_address_required and self.shipping_address:
            shipping_done = True
        elif shipping_address_required and not self.shipping_address:
            shipping_done = False
        else:
            shipping_done = True

        billing_profile = self.billing_profile
        # shipping_address = self.shipping_address
        billing_address = self.billing_address
        total = self.total
        if billing_profile and shipping_done and billing_address and total > 0:
            return True
        return False

    def update_purchases(self):
        for product in self.cart.products.all():
            obj, created = ProductPurchase.objects.get_or_create(
                order_id = self.order_id,
                product = product,
                billing_profile = self.billing_profile
            )
            # obj.refunded = False
            # obj.save()
        return ProductPurchase.objects.filter(order_id = self.order_id).count()

    def mark_paid(self):
        if self.status != 'paid':
            if self.check_done():
                self.status = 'paid'
                self.save()
                self.update_purchases()
        return self.status

def pre_save_create_order_id(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)
    qs = Order.objects.filter(cart = instance.cart).exclude(billing_profile = instance.billing_profile)
    if qs.exists():
        qs.update(active = False)

pre_save.connect(pre_save_create_order_id, sender = Order)

def post_save_cart_total(sender, instance, created, *args, **kwargs):
    if not created:
        cart_obj = instance
        cart_total = cart_obj.total
        cart_id = cart_obj.id
        qs = Order.objects.filter(cart__id = cart_id)
        if qs.count() == 1:
            order_obj = qs.first()
            order_obj.update_total()

post_save.connect(post_save_cart_total, sender = Cart)

def post_save_order(sender, instance, created, *args, **kwargs):
    if created:
        instance.update_total()

post_save.connect(post_save_order, sender = Order)

class ProductPurchaseQuerySet(models.QuerySet):
    def active(self):
        return self.filter(refunded = False)

    def digital(self):
        return self.filter(product__is_digital = True)

    def by_billing_profile(self, request):
        billing_profile, created = BillingProfile.objects.new_or_get(request)
        return self.filter(billing_profile = billing_profile)

class ProductPurchaseManager(models.Manager):
    def get_queryset(self):
        return ProductPurchaseQuerySet(self.model, using = self._db)

    def all(self):
        return self.get_queryset().active()

    def digital(self):
        return self.get_queryset().active().digital()

    def by_billing_profile(self, request):
        return self.get_queryset().by_billing_profile(request)

    def products_by_id(self, request):
        qs = self.by_billing_profile(request).digital()
        product_ids = [obj.product.id for obj in qs]
        return product_ids

    def products_by_request(self, request):
        ids_ = self.products_by_id(request)
        product_qs = Product.objects.filter(id__in = ids_).distinct()
        return product_qs

class ProductPurchase(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, on_delete = models.CASCADE)
    order_id = models.CharField(max_length = 120)
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    refunded = models.BooleanField(default = False)
    updated = models.DateTimeField(auto_now = True)
    timestamp = models.DateTimeField(auto_now_add = True)

    objects = ProductPurchaseManager()

    def __str__(self):
        return self.product.title