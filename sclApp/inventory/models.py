from django.db import models
from sclApp.accounts.models import CustomUser

class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self): return self.name

class Item(models.Model):
    CATEGORY_CHOICES = [
        ('TOOL', 'Tool/Equipment (Returnable)'),
        ('CONS', 'Consumable (Non-Returnable)'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=4, choices=CATEGORY_CHOICES, default='TOOL')
    quantity = models.IntegerField(default=0)
    unit = models.CharField(max_length=20, help_text="e.g., kg, Liters, Pieces")
    min_stock_level = models.IntegerField(default=5, help_text="Alert when stock hits this")

    def __str__(self): 
        return f"{self.name} ({self.quantity} {self.unit})"

class StoreTransaction(models.Model):
    TRANSACTION_TYPES = [('IN', 'Restock'), ('OUT', 'Collection')]
    DEPARTMENTS = [
        ('GH', 'Greenhouse'),
        ('OF', 'Open Field'),
        ('LS', 'Livestock'),
        ('AD', 'Admin'),
    ]
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    staff = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    receiver_name = models.CharField(max_length=100, null =True, help_text="Who is physically taking the item?")
    department = models.CharField(max_length=2, null=True, choices=DEPARTMENTS, default='GH')
    is_returnable = models.BooleanField(default=False, help_text="Is this a tool that must be returned?")
    is_returned = models.BooleanField(default=False)
    
    returned_at = models.DateTimeField(null=True, blank=True)
    quantity_returned = models.IntegerField(default=0)

    quantity = models.IntegerField()
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
    # Only adjust stock if this is a BRAND NEW record (pk is None)
        if not self.pk:
            if self.transaction_type == 'IN':
                self.item.quantity += self.quantity
            else:
                self.item.quantity -= self.quantity
            self.item.save()
        
        # If the record already exists (an update), the View handles the math 
        # for returns, so we just save the transaction details here.
        super().save(*args, **kwargs)


    @property
    def remaining_to_return(self):
        # Use .get() or handle None to prevent errors
        qty = self.quantity or 0
        returned = self.quantity_returned or 0
        return qty - returned

    # @property
    # def remaining_to_return(self):
    #     return self.quantity - self.quantity_returned

    def __str__(self):
        return f"{self.staff.username} - {self.transaction_type} - {self.item.name}"