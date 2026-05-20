from django.db import models
from sclApp.accounts.models import CustomUser
from django.db.models import Sum

# =========================================================================
# 1. THE PRODUCTION AREA (Where are we planting?)
# =========================================================================
class ProductionArea(models.Model):
    AREA_TYPES = [
        ('GH1', 'Greenhouse 1 (Bays 1-11)'),
        ('GH2', 'Greenhouse 2 (Bays 1-12)'),
        ('OPEN', 'Open Field (1.5 Hectares)'),
    ]
    
    area_type = models.CharField(max_length=5, choices=AREA_TYPES)
    bay_number = models.IntegerField(null=True, blank=True, help_text="Leave blank if Open Field")
    is_active = models.BooleanField(default=True, help_text="Is this space currently usable?")

    class Meta:
        ordering = ['area_type', 'bay_number']
        unique_together = ['area_type', 'bay_number'] # Prevents duplicating 'Greenhouse 1, Bay 1'

    def __str__(self):
        if self.area_type == 'OPEN':
            return "Open Field"
        return f"{self.get_area_type_display()} - Bay {self.bay_number}"


# =========================================================================
# 2. THE CROP BATCH (What living plant cycle are we tracking?)
# =========================================================================
class CropBatch(models.Model):
    CROP_CHOICES = [
        ('TOMATO', 'Tomato'),
        ('SWEET_PEPPER', 'Sweet Pepper'),
        ('HABANERO', 'Habanero Pepper'),
        ('CUCUMBER', 'Cucumber'),
    ]
    
    crop_type = models.CharField(max_length=20, choices=CROP_CHOICES)
    variety = models.CharField(max_length=50, help_text="e.g., Eva F1, Habanero Red, etc.")
    location = models.ForeignKey(ProductionArea, on_delete=models.CASCADE, related_name='crops')
    
    plant_count = models.IntegerField(help_text="Number of seedlings transplanted")
    transplant_date = models.DateField()
    
    expected_yield_per_plant = models.DecimalField(
        max_digits=5, decimal_places=2, default=4.00,
        help_text="Expected yield in kilograms per plant for this cycle (e.g., 4.00)"
    )

    is_harvested = models.BooleanField(default=False, help_text="Check when the entire lifecycle is completed")
    notes = models.TextField(blank=True, null=True)

    # A quick property method to calculate total target output for the entire bay
    @property
    def total_expected_yield(self):
        return self.plant_count * float(self.expected_yield_per_plant)

    @property
    def total_harvested_weight(self):
        """
        Looks up the HarvestLog table, finds all records matching THIS specific 
        batch cycle, and sums up the total kilograms automatically.
        """
        # 'harvests' is the related_name we defined on the HarvestLog foreign key
        total = self.harvests.aggregate(total=Sum('quantity_harvested'))['total']
        return float(total) if total else 0.0

    @property
    def calculate_performance_percentage(self):
        """Determines how far along the progress bar should fill up (0% to 100%)"""
        if self.total_expected_yield <= 0:
            return 0
        
        percentage = (self.total_harvested_weight / self.total_expected_yield) * 100
        return min(round(percentage, 1), 100) # Prevents the bar from overflowing past 100% visually
    

    def __str__(self):
        return f"{self.variety} ({self.get_crop_type_display()}) at {self.location}"


class HarvestLog(models.Model):
    batch = models.ForeignKey(CropBatch, on_delete=models.CASCADE, related_name='harvests')
    date_harvested = models.DateField()
    
    # Actual weight brought to store/sorting center
    quantity_harvested = models.DecimalField(
        max_digits=7, decimal_places=2, 
        help_text="Weight recorded in Kilograms (KG)"
    )
    
    grade_a_percentage = models.IntegerField(
        default=100, 
        help_text="Percentage of premium, market-ready produce (0-100)"
    )
    
    logged_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True
    )
    remarks = models.TextField(blank=True, null=True, help_text="e.g., First flush picking, minor blossom end rot noticed")

    def __str__(self):
        return f"{self.quantity_harvested} KG from {self.batch} on {self.date_harvested}"
# =========================================================================
# 3. ORGANIC SPRAYING & IPM LOG (Protecting the crop sustainably)
# =========================================================================
class SprayingLog(models.Model):
    APPLICATION_TYPES = [
        ('PREV', 'Preventative (Routine Schedule)'),
        ('CURA', 'Curative (Active Outbreak Attack)'),
    ]
    
    batch = models.ForeignKey(CropBatch, on_delete=models.CASCADE, related_name='sprays')
    date_applied = models.DateField()
    application_type = models.CharField(max_length=4, choices=APPLICATION_TYPES, default='PREV')
    
    # Botanical / Organic Remedy inputs
    remedy_used = models.CharField(max_length=100, help_text="e.g., Neem Oil Extract, Tephrosia Leaf Extract, Wood Ash mixture")
    dosage = models.CharField(max_length=50, help_text="e.g., 50ml per 20L Knapsack")
    
    target_pest_disease = models.CharField(max_length=150, help_text="e.g., Tuta Absoluta, Whiteflies, Aphids, Downy Mildew")
    operator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, help_text="Who sprayed it?")
    observations = models.TextField(blank=True, null=True, help_text="Crop response or pest mortality observations")

    def __str__(self):
        return f"{self.remedy_used} on {self.batch} ({self.date_applied})"

# =========================================================================
# 4. Daily Activity record
# =========================================================================

class DailyActivityLog(models.Model):
    ACTIVITY_CHOICES = [
        ('BEDP', 'Bed Preparation / Soil Amendment'),
        ('PRUN', 'Pruning / Defoliation / Suckering'),
        ('STAK', 'Staking / Trellising / Twisting'),
        ('WEED', 'Weeding / Sanitation'),
        ('SCOO', 'Scooping (Manual Pest/Debris Removal)'),
        ('SCOU', 'Pest & Disease Scouting'),
        ('SPRA', 'Spraying Application Routine'),
        ('HARV', 'Harvesting Operation'),
        ('FERT', 'Fertilization / Fertigation'),
        ('IRRI', 'Irrigation System Maintenance'),
        ('OTHR', 'Other General Maintenance'),
    ]

    batch = models.ForeignKey(CropBatch, on_delete=models.CASCADE, related_name='activities', help_text="Select the crop batch/bay")
    date_logged = models.DateField(auto_now_add=True)  # Automatically logs the current date
    activity_type = models.CharField(max_length=4, choices=ACTIVITY_CHOICES)
    description = models.TextField(help_text="Details of work done or observations made (e.g., pruned lower leaves, spotted early whitefly activity)")
    man_hours = models.DecimalField(max_digits=4, decimal_places=1, default=1.0, help_text="Estimated hours spent on this task")
    logged_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.get_activity_type_display()} at {self.batch.location} on {self.date_logged}"