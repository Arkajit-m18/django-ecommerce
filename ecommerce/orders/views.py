from django.shortcuts import render, Http404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Order
from billing.models import BillingProfile

# Create your views here.
class OrderListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        return Order.objects.by_billing_profile(request = self.request).not_created()

class OrderDetailView(LoginRequiredMixin, DetailView):
    def get_object(self):
        qs = Order.objects.by_billing_profile(request = self.request).filter(order_id = self.kwargs.get('order_id'))
        if qs.count() == 1:
            return qs.first()
        raise Http404('Order does not exist')
