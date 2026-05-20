from django.db import models
from django.utils import timezone

class LivestockGroup(models.Model):
    ANIMAL_TYPES = [
        ('POULTRY', 'Poultry (Poultry/Layers/Broilers)'),
        ('PIGGERY', 'Piggery'),
        ('CATTLE', 'Cattle'),
        ('SMALL_RUM', 'Small Ruminants (Goats/Sheep)'),
        ('AQUACULTURE', 'Aquaculture (Fish)'),
    ]
    
    STAGE_CHOICES = [
        ('YOUNG', 'Young / Chicks / Weaners'),
        ('GROWING', 'Growing / Growers / Fingerlings'),
        ('MATURE_PROD', 'Mature Production (Layers / Milking)'),
        ('MATURE_MEAT', 'Mature Fattening (Broilers / Market Size)'),
        ('BREEDER', 'Breeder Stock'),
    ]

    name_or_tag = models.CharField(max_length=100, unique=True, help_text="e.g., Pen 4 Layers, Sow #12, Batch B Broilers")
    animal_type = models.CharField(max_length=15, choices=ANIMAL_TYPES)
    stage = models.CharField(max_length=15, choices=STAGE_CHOICES)
    breed = models.CharField(max_length=100, blank=True, help_text="e.g., Kalahari Red, Noiler, Large White")
    
    # Quantities
    initial_count = models.IntegerField(default=1)
    current_count = models.IntegerField(default=1, help_text="Auto-updates based on mortalities/sales")
    
    # Location tracking on the farm
    housing_location = models.CharField(max_length=100, help_text="e.g., Pen 2, Coop A, Paddock 5")
    created_at = models.DateTimeField(auto_now_add=True)
    date_acquired = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True, help_text="Uncheck if the batch is completely sold or processed")
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name_or_tag} - {self.get_animal_type_display()} ({self.current_count} head)"


class DailyLog(models.Model):
    """
    A unified daily log to capture mortality, feed tracking, and health status 
    for any livestock group in a single database hit.
    """
    group = models.ForeignKey(LivestockGroup, on_delete=models.CASCADE, related_name='daily_logs')
    date = models.DateField(default=timezone.now)
    
    # Vital Stats
    mortality = models.IntegerField(default=0, help_text="Number of animal deaths today")
    avg_weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="In kg (Optional tracker)")
    
    # Feed tracking
    feed_type_used = models.CharField(max_length=100, blank=True, help_text="e.g., Layer Mash, Starter Pellets")
    feed_quantity_kg = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    
    # Health & Treatment
    health_status = models.CharField(max_length=20, choices=[('EXCELLENT', 'Excellent'), ('STABLE', 'Stable'), ('ALERT', 'Sick/Alert')], default='EXCELLENT')
    medication_administered = models.CharField(max_length=150, blank=True, help_text="e.g., Gumboro Vaccine, Tylosin")
    
    notes = models.TextField(blank=True, help_text="General observations (e.g., wet litter, drop in feed intake)")

    class Meta:
        ordering = ['-date']
        unique_together = ('group', 'date') # Prevents double entries for the same group on the same day

    def save(self, *args, **kwargs):
        # Automatically deduct mortalities from the live group population count
        if self.pk is None and self.mortality > 0:
            self.group.current_count = models.F('current_count') - self.mortality
            self.group.save()
        super().save(*args, **kwargs)


class ProductionYield(models.Model):
    """
    Captures commercial outputs from the livestock units (Eggs, Milk, Fish Harvest).
    """
    YIELD_TYPES = [
        ('EGGS', 'Eggs (Crates)'),
        ('MILK', 'Milk (Liters)'),
        ('MEAT', 'Live Weight Sold (kg)'),
        ('MANURE', 'Manure (Bags)'),
    ]
    group = models.ForeignKey(LivestockGroup, on_delete=models.CASCADE, related_name='production_yields')
    date = models.DateField(default=timezone.now)
    yield_type = models.CharField(max_length=10, choices=YIELD_TYPES)
    
    quantity_good = models.DecimalField(max_digits=7, decimal_places=2, help_text="Main sellable yield count")
    quantity_damaged = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="e.g., cracked eggs, spilled milk")

    def __str__(self):
        return f"{self.date} | {self.group.name_or_tag} - {self.quantity_good} {self.get_yield_type_display()}"