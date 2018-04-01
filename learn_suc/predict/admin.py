from django.contrib import admin

from .models import Type, Item, Embedding

# Register your models here.

admin.site.register([Type, Item, Embedding])