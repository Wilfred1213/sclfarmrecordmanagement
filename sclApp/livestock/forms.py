from django import forms
from .models import LivestockGroup, DailyLog, ProductionYield

class LivestockGroupForm(forms.ModelForm):
    class Meta:
        model = LivestockGroup
        fields = ['name_or_tag', 'animal_type', 'stage', 'breed', 'initial_count', 'housing_location']
        widgets = {
            'name_or_tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Pen 4 Layers, Sow #12'}),
            'animal_type': forms.Select(attrs={'class': 'form-select'}),
            'stage': forms.Select(attrs={'class': 'form-select'}),
            'breed': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Noiler, Large White'}),
            'initial_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'housing_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Pen 3 Bay B'}),
        }


class DailyLogForm(forms.ModelForm):
    class Meta:
        model = DailyLog
        fields = ['group', 'mortality', 'health_status', 'feed_type_used', 'feed_quantity_kg', 'notes']
        widgets = {
            'group': forms.Select(attrs={'class': 'form-select'}),
            'mortality': forms.NumberInput(attrs={'class': 'form-control border-danger-subtle', 'min': 0}),
            'health_status': forms.Select(attrs={'class': 'form-select'}),
            'feed_type_used': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Layer Mash'}),
            'feed_quantity_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Daily health observations...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].queryset = LivestockGroup.objects.filter(is_active=True)
        self.fields['group'].empty_label = "-- Select Active Group --"


class ProductionYieldForm(forms.ModelForm):
    class Meta:
        model = ProductionYield
        fields = ['group', 'yield_type', 'quantity_good', 'quantity_damaged']
        widgets = {
            'group': forms.Select(attrs={'class': 'form-select'}),
            'yield_type': forms.Select(attrs={'class': 'form-select'}),
            'quantity_good': forms.NumberInput(attrs={'class': 'form-control border-success-subtle', 'step': '0.01'}),
            'quantity_damaged': forms.NumberInput(attrs={'class': 'form-control border-danger-subtle', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].queryset = LivestockGroup.objects.filter(is_active=True)
        self.fields['group'].empty_label = "-- Select Producing Group --"