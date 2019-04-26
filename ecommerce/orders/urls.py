from django.urls import path

from .views import OrderListView, OrderDetailView

app_name = 'orders'

urlpatterns = [
    path('', OrderListView.as_view(), name = 'all-orders'),
    path('<str:order_id>/', OrderDetailView.as_view(), name = 'single-order'),
]