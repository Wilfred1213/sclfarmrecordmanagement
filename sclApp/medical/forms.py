from django import forms
from sclApp.medical.models import StaffMedicalCase, StaffTreatmentLog
# from sclApp.medical.forms import StaffMedicalCaseForm, StaffTreatmentLogForm
from django.contrib.auth import get_user_model

User = get_user_model()

class StaffMedicalCaseForm(forms.ModelForm):
    class Meta:
        model = StaffMedicalCase
        fields = ['staff_member', 'case_type', 'chief_complaint', 'clinical_notes', 'status', 'recommended_sick_days']
        widgets = {
            'staff_member': forms.Select(attrs={'class': 'form-select'}),
            'case_type': forms.Select(attrs={'class': 'form-select'}),
            'chief_complaint': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Sharp laceration on left hand, High fever'}),
            'clinical_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter comprehensive vitals, symptoms, or accident sequence details...'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'recommended_sick_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['staff_member'].empty_label = "-- Select Employee --"


class StaffTreatmentLogForm(forms.ModelForm):
    class Meta:
        model = StaffTreatmentLog
        fields = ['medical_case', 'medication_or_first_aid', 'dosage_or_action', 'administered_by', 'next_review_date']
        widgets = {
            'medical_case': forms.Select(attrs={'class': 'form-select'}),
            'medication_or_first_aid': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Paracetamol, Wound Dressing, Hospital Referral'}),
            'dosage_or_action': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 500mg TDS, Applied sterile bandage'}),
            'administered_by': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Clinic Staff / Safety Lead'}),
            'next_review_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['medical_case'].queryset = StaffMedicalCase.objects.exclude(status='RESOLVED').order_by('-created_at')
        self.fields['medical_case'].empty_label = "-- Select Active Case File --"