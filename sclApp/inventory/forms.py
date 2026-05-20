from django import forms
from .models import Item, StoreTransaction


class ReturnForm(forms.Form):
    return_quantity = forms.IntegerField(min_value=1)


class TransactionForm(forms.ModelForm):
    class Meta:
        model = StoreTransaction
        # Include the new tracking fields
        fields = ['item', 'transaction_type', 'receiver_name', 'department', 'quantity', 'is_returnable', 'notes']
        
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'receiver_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Who is taking/bringing this?'
            }),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': '2'}),
            # Checkbox for returnable items (tools)
            'is_returnable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customizing labels to make it clearer for the Store Officer
        self.fields['receiver_name'].label = "Receiver / Supplier Name"
        self.fields['is_returnable'].label = "Is this a tool to be returned?"

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        quantity = cleaned_data.get('quantity')
        t_type = cleaned_data.get('transaction_type')

        # Logic: If it's a collection and we don't have enough...
        if t_type == 'OUT' and item and quantity:
            if item.quantity < quantity:
                raise forms.ValidationError(
                    f"Insufficient Stock! You are trying to collect {quantity} {item.unit}, "
                    f"but only {item.quantity} remains in the store."
                )
        return cleaned_data

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'category', 'quantity', 'unit', 'min_stock_level']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Kg, Liters, Bags'}),
            'min_stock_level': forms.NumberInput(attrs={'class': 'form-control'}),
        }