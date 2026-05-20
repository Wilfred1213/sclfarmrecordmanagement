from django.contrib import admin
from .models import ProductionArea, CropBatch, SprayingLog

@admin.register(ProductionArea)
class ProductionAreaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'area_type', 'bay_number', 'is_active')
    list_filter = ('area_type', 'is_active')
    search_fields = ('bay_number',)
    list_editable = ('is_active',)  # Quickly toggle bay usability from the list view


@admin.register(CropBatch)
class CropBatchAdmin(admin.ModelAdmin):
    list_display = ('variety', 'crop_type', 'location', 'plant_count', 'transplant_date', 'is_harvested')
    list_filter = ('crop_type', 'is_harvested', 'location__area_type')
    search_fields = ('variety', 'notes')
    list_editable = ('is_harvested',)  # Easily check off completed cycles
    date_hierarchy = 'transplant_date'  # Adds a nice calendar timeline navigation header


@admin.register(SprayingLog)
class SprayingLogAdmin(admin.ModelAdmin):
    list_display = ('remedy_used', 'batch', 'application_type', 'target_pest_disease', 'date_applied', 'operator')
    list_filter = ('application_type', 'date_applied', 'batch__location')
    search_fields = ('remedy_used', 'target_pest_disease', 'observations')
    date_hierarchy = 'date_applied'
    
    # This automatically fills the 'operator' field with the logged-in admin user saving the form
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only set on initial creation
            obj.operator = request.user
        super().save(request, obj, form, change)