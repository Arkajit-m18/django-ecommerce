from django.shortcuts import render, Http404
from django.views.generic import (
    ListView,
    DetailView,
)

from .models import Product
from carts.models import Cart

# Create your views here.
class ProductListView(ListView):
    model = Product

class ProductDetailView(DetailView):
    model = Product

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        request = self.request
        instance = Product.objects.get_by_id(pk)
        if instance is None:
            raise Http404("Product doesn't exist!")
        return instance

class ProductSlugDetailView(DetailView):
    model = Product

    
    def get_context_data(self, **kwargs):
        context = super(ProductSlugDetailView, self).get_context_data(**kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        return context
    

    def get_object(self, *args, **kwargs):
        slug = self.kwargs.get('slug')
        request = self.request
        instance = Product.objects.get_by_slug(slug)
        if instance is None:
            raise Http404("Product doesn't exist!")
        return instance

class ProductFeaturedListView(ListView):
    template_name = 'products/product_featured_list.html'
    model = Product

    def get_queryset(self):
        queryset = Product.objects.all()
        return queryset.featured()
        
        # queryset = super().get_queryset()
        # return queryset.filter(featured = True)

class ProductFeaturedDetailView(DetailView):
    template_name = 'products/product_featured_detail.html'
    model = Product

    def get_queryset(self):
        queryset = Product.objects.all()
        return queryset.featured()

        # queryset = super().get_queryset()
        # return queryset.filter(featured = True)

class ProductSlugFeaturedDetailView(DetailView):
    template_name = 'products/product_featured_detail.html'
    model = Product

    def get_queryset(self):
        queryset = Product.objects.all()
        return queryset.featured()