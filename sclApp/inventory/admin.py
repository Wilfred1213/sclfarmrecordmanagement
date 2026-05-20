from django.contrib import admin
from sclApp.inventory.models import Item, StoreTransaction, Category

# Register your models here.
# admin.site.register([Item, StoreTransaction, Category])


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity', 'unit', 'min_stock_level')
    list_filter = ('category',)
    search_fields = ('name',)

admin.site.register(Category)
admin.site.register(StoreTransaction)