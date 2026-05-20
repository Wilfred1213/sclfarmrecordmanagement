from django import forms
from .models import CropBatch, SprayingLog, ProductionArea, HarvestLog, DailyActivityLog

# =========================================================================
# 1. CROP BATCH REGISTRATION FORM
# =========================================================================
class CropBatchForm(forms.ModelForm):
    class Meta:
        model = CropBatch
        fields = ['crop_type', 'variety', 'location', 'plant_count', 'transplant_date', 'notes']
        
        widgets = {
            'crop_type': forms.Select(attrs={'class': 'form-select py-2'}),
            'variety': forms.TextInput(attrs={
                'class': 'form-control py-2', 
                'placeholder': 'e.g., Eva F1, Habanero Red'
            }),
            'location': forms.Select(attrs={'class': 'form-select py-2'}),
            'plant_count': forms.NumberInput(attrs={
                'class': 'form-control py-2', 
                'placeholder': 'Total seedlings transplanted'
            }),
            'transplant_date': forms.DateInput(attrs={
                'class': 'form-control py-2', 
                'type': 'date'  # Forces a native interactive mobile calendar popup
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Add details on seedling health, nursery duration, etc.'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only display production spaces that are marked as active in the farm inventory
        self.fields['location'].queryset = ProductionArea.objects.filter(is_active=True)


# =========================================================================
# 2. ORGANIC SPRAYING & IPM LOG FORM
# =========================================================================
class SprayingLogForm(forms.ModelForm):
    class Meta:
        model = SprayingLog
        fields = ['batch', 'date_applied', 'application_type', 'remedy_used', 'dosage', 'target_pest_disease', 'observations']
        
        widgets = {
            'batch': forms.Select(attrs={'class': 'form-select py-2'}),
            'date_applied': forms.DateInput(attrs={
                'class': 'form-control py-2', 
                'type': 'date'
            }),
            'application_type': forms.Select(attrs={'class': 'form-select py-2'}),
            'remedy_used': forms.TextInput(attrs={
                'class': 'form-control py-2', 
                'placeholder': 'e.g., Neem Oil, Tephrosia Extract, Garlic-Chili spray'
            }),
            'dosage': forms.TextInput(attrs={
                'class': 'form-control py-2', 
                'placeholder': 'e.g., 50ml per 20L Knapsack'
            }),
            'target_pest_disease': forms.TextInput(attrs={
                'class': 'form-control py-2', 
                'placeholder': 'e.g., Tuta Absoluta, Whiteflies, Thrips'
            }),
            'observations': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Note crop reaction or pest population changes observed...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show crop batches that haven't been completely cleared out or harvested yet
        self.fields['batch'].queryset = CropBatch.objects.filter(is_harvested=False).select_related('location')


class HarvestLogForm(forms.ModelForm):
    class Meta:
        model = HarvestLog
        fields = ['batch', 'date_harvested', 'quantity_harvested', 'grade_a_percentage', 'remarks']
        widgets = {
            'batch': forms.Select(attrs={'class': 'form-select py-2'}),
            'date_harvested': forms.DateInput(attrs={
                'class': 'form-control py-2', 
                'type': 'date'
            }),
            'quantity_harvested': forms.NumberInput(attrs={
                'class': 'form-control py-2', 
                'placeholder': 'Weight in KG (e.g., 45.50)',
                'step': '0.01'
            }),
            'grade_a_percentage': forms.NumberInput(attrs={
                'class': 'form-control py-2', 
                'placeholder': 'e.g., 90',
                'min': '0', 'max': '100'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'e.g., First flush picking, high quality'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active, unharvested crops in the dropdown
        self.fields['batch'].queryset = CropBatch.objects.filter(is_harvested=False).select_related('location')


class DailyActivityLogForm(forms.ModelForm):
    class Meta:
        model = DailyActivityLog
        fields = ['batch', 'activity_type', 'description', 'man_hours']
        widgets = {
            'batch': forms.Select(attrs={'class': 'form-select py-2'}),
            'activity_type': forms.Select(attrs={'class': 'form-select py-2'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Be specific: e.g., Tied vines on row 3, removed suckers, or cleared weed perimeter.'
            }),
            'man_hours': forms.NumberInput(attrs={'class': 'form-control py-2', 'step': '0.5'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['batch'].queryset = CropBatch.objects.filter(is_harvested=False).select_related('location')