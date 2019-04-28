from django.db import models
from django.urls import reverse
from django.db.models import Q
from django.db.models.signals import pre_save, post_save

from ecommerce.utils import unique_slug_generator

import random, os

def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext

def upload_image_path(instance, filename):
    new_filename = random.getrandbits(32)
    name, ext = get_filename_ext(filename)
    final_filename = f'{new_filename}{ext}'
    return f'products/{new_filename}/{final_filename}'

class ProductQuerySet(models.QuerySet):
    def featured(self):
        return self.filter(featured = True)

    def active(self):
        return self.filter(active = True)

    def search(self, query_param):
        lookups = (
            Q(title__icontains = query_param) | Q(description__icontains = query_param) | 
            Q(price__icontains = query_param) |
            Q(tag__title__icontains = query_param)
        )

        return self.filter(lookups).distinct()

class ProductManager(models.Manager):

    def get_queryset(self):
        return ProductQuerySet(self.model, using = self._db)

    def all(self):
        return self.get_queryset().active()

    def featured(self):
        return self.get_queryset().featured()

    def get_by_id(self, pk):
        qs = self.get_queryset().filter(pk = pk)
        if qs.count() == 1:
            return qs.first()
        return None

    def get_by_slug(self, slug):
        qs = self.get_queryset().filter(slug = slug)
        if qs.count() == 1:
            return qs.first()
        return None

    def search(self, query_param):
        return self.get_queryset().active().search(query_param)

# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length = 256)
    slug = models.SlugField(blank = True, unique = True)
    description = models.TextField()
    price = models.DecimalField(decimal_places = 2, max_digits = 10)
    image = models.ImageField(upload_to = upload_image_path, null = True, blank = True)
    featured = models.BooleanField(default = False)
    active = models.BooleanField(default = True)
    timestamp = models.DateTimeField(auto_now_add = True)

    objects = ProductManager()

    def get_absolute_url(self):
        return reverse('products:single_product', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-timestamp']

def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(product_pre_save_receiver, sender = Product)