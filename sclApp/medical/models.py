from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class StaffMedicalCase(models.Model):
    CASE_TYPE_CHOICES = [
        ('WORK_INJURY', 'Work-Related Injury'),
        ('ROUTINE_ILLNESS', 'General Illness (Malaria, Typhoid, etc.)'),
        ('EXPOSURE', 'Chemical/Bio-Product Exposure'),
        ('FITNESS_CHECK', 'Routine Medical Fitness Clearance'),
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Under Observation / Active Case'),
        ('SICK_LEAVE', 'On Approved Sick Leave'),
        ('RESOLVED', 'Fit for Duty / Resolved'),
    ]

    # Links directly to your actual system user/staff account
    staff_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medical_files')
    case_type = models.CharField(max_length=30, choices=CASE_TYPE_CHOICES)
    incident_date = models.DateField(default=timezone.now, help_text="Date illness reported or injury occurred")
    
    chief_complaint = models.CharField(max_length=250, help_text="Summary of what the staff is experiencing or the injury")
    clinical_notes = models.TextField(blank=True, null=True, help_text="Symptoms, diagnosis details, or incident description")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    recommended_sick_days = models.PositiveIntegerField(default=0, help_text="Number of days ordered off-duty by clinician")
    return_to_work_date = models.DateField(blank=True, null=True, editable=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Automatically calculate target return date if sick leave is granted
        if self.recommended_sick_days > 0:
            self.return_to_work_date = self.incident_date + timezone.timedelta(days=self.recommended_sick_days)
        else:
            self.return_to_work_date = self.incident_date
        super().save(*args, **kwargs)

    class Meta:
        app_label = 'medical'

    def __str__(self):
        return f"{self.staff_member.get_full_name() or self.staff_member.username} - {self.get_case_type_display()}"


class StaffTreatmentLog(models.Model):
    medical_case = models.ForeignKey(StaffMedicalCase, on_delete=models.CASCADE, related_name='treatments')
    treatment_date = models.DateTimeField(default=timezone.now)
    medication_or_first_aid = models.CharField(max_length=200, help_text="Administered drugs, dressings, or clinic referrals")
    dosage_or_action = models.CharField(max_length=100, help_text="e.g., 500mg, Rest, Referred to General Hospital")
    administered_by = models.CharField(max_length=100, help_text="Name of Medical Officer or Safety Warden in charge")
    next_review_date = models.DateField(blank=True, null=True, help_text="Follow-up clinical evaluation date if needed")

    class Meta:
        app_label = 'medical'
    def __str__(self):
        return f"Treatment on {self.treatment_date.strftime('%Y-%m-%d')} by {self.administered_by}"