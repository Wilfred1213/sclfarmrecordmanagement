from django.contrib import admin
from django.utils import timezone
from sclApp.medical.models import StaffMedicalCase, StaffTreatmentLog

class StaffTreatmentLogInline(admin.TabularInline):
    model = StaffTreatmentLog
    extra = 1
    # Swapped veterinary fields for human treatment tracking fields
    fields = ('treatment_date', 'medication_or_first_aid', 'dosage_or_action', 'administered_by', 'next_review_date')


@admin.register(StaffMedicalCase)
class StaffMedicalCaseAdmin(admin.ModelAdmin):
    # Displays clean employee metrics on the main ledger index row
    list_display = ('staff_member', 'case_type', 'incident_date', 'status', 'recommended_sick_days', 'is_currently_off_duty')
    
    # Sidebar quick filters for management audits
    list_filter = ('status', 'case_type', 'incident_date')
    
    # Fast database lookup search bars
    search_fields = ('staff_member__username', 'staff_member__first_name', 'staff_member__last_name', 'chief_complaint')
    
    # Sort history chronologically by default (newest incidents at the top)
    ordering = ('-incident_date',)
    
    # Embed treatment logs so you can update treatment records directly inside the case file
    inlines = [StaffTreatmentLogInline]
    
    fieldsets = (
        ('Personnel Dossier', {
            'fields': ('staff_member', 'case_type', 'status')
        }),
        ('Clinical & Incident Assessment', {
            'fields': ('chief_complaint', 'clinical_notes', 'incident_date', 'recommended_sick_days')
        }),
    )

    # Custom indicator method to see who is currently active on their sick leave window
    def is_currently_off_duty(self, obj):
        if obj.status == 'SICK_LEAVE' and obj.return_to_work_date:
            return obj.return_to_work_date >= timezone.now().date()
        return False
    is_currently_off_duty.boolean = True
    is_currently_off_duty.short_description = 'On Active Sick Leave'