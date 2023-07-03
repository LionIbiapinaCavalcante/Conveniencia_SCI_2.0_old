from django.contrib import admin
from .models import RegistroCompra, ItemCompra

class ItemCompraInline(admin.TabularInline):
    model = ItemCompra

@admin.register(RegistroCompra)
class RegistroCompraAdmin(admin.ModelAdmin):
    inlines = [ItemCompraInline]