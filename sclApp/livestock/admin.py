from django.contrib import admin
from .models import LivestockGroup, DailyLog, ProductionYield

@admin.register(LivestockGroup)
class LivestockGroupAdmin(admin.ModelAdmin):
    # Columns displayed in the main list view
    list_display = ('name_or_tag', 'animal_type', 'stage', 'current_count', 'initial_count', 'housing_location', 'is_active')
    
    # Clickable fields to enter the edit page
    list_display_links = ('name_or_tag',)
    
    # Right-side filter sidebar options
    list_filter = ('animal_type', 'stage', 'is_active', 'housing_location')
    
    # Search bar targets
    search_fields = ('name_or_tag', 'breed', 'housing_location')
    
    # Default order (newest batches first)
    ordering = ('-created_at',)
    
    # Organizes edit page fields into scannable structural sections
    fieldsets = (
        ('Core Identification', {
            'fields': ('name_or_tag', 'animal_type', 'breed')
        }),
        ('Inventory & Location Tracking', {
            'fields': ('initial_count', 'current_count', 'housing_location', 'stage', 'is_active')
        }),
    )
    
    # Read-only configuration to avoid accidentally manipulating critical calculated fields directly
    readonly_fields = ('created_at',)


@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = ('group', 'date', 'health_status', 'mortality', 'feed_type_used', 'feed_quantity_kg')
    list_filter = ('date', 'health_status', 'group__animal_type')
    search_fields = ('group__name_or_tag', 'notes', 'feed_type_used')
    ordering = ('-date', '-id')
    
    fieldsets = (
        ('Log Metadata', {
            'fields': ('group', 'date')
        }),
        ('Health & Vital Performance Metrics', {
            'fields': ('mortality', 'health_status')
        }),
        ('Feeding Adjustments', {
            'fields': ('feed_type_used', 'feed_quantity_kg')
        }),
        ('Field Observations', {
            'fields': ('notes',)
        }),
    )


@admin.register(ProductionYield)
class ProductionYieldAdmin(admin.ModelAdmin):
    list_display = ('group', 'date', 'yield_type', 'quantity_good', 'quantity_damaged', 'total_yield')
    list_filter = ('yield_type', 'date', 'group__animal_type')
    search_fields = ('group__name_or_tag', 'yield_type')
    ordering = ('-date', '-id')

    # Calculated field method to show total combined yield in the list view row
    def total_yield(self, obj):
        return obj.quantity_good + obj.quantity_damaged
    total_yield.short_description = 'Total Output Collected'