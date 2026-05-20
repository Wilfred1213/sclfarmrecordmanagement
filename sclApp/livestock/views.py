from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Sum
from .models import LivestockGroup, DailyLog, ProductionYield
from .forms import LivestockGroupForm, DailyLogForm, ProductionYieldForm

def livestock_dashboard(request):
    toast_message = ""
    toast_status = "success"
    today = timezone.now().date()

    if request.method == 'POST':
        # PROCESS ACTION 1: Register New Group
        if 'register_batch' in request.POST:
            form = LivestockGroupForm(request.POST)
            if form.is_valid():
                batch = form.save(commit=False)
                batch.current_count = batch.initial_count
                batch.save()
                toast_message = f"Batch '{batch.name_or_tag}' successfully opened."
            else:
                toast_status = "error"
                toast_message = "Could not register batch. Please review input metrics."

        # PROCESS ACTION 2: Daily Maintenance Entry 
        elif 'log_daily' in request.POST:
            form = DailyLogForm(request.POST)
            if form.is_valid():
                log = form.save()
                toast_message = f"Daily sheet processed for {log.group.name_or_tag}."
            else:
                toast_status = "error"
                toast_message = "Save failed. Check if a duplicate entry exists for today."

        # PROCESS ACTION 3: Production Ledger Tracking Entry
        elif 'record_yield' in request.POST:
            form = ProductionYieldForm(request.POST)
            if form.is_valid():
                prod_yield = form.save()
                toast_message = f"Production metrics successfully captured."
            else:
                toast_status = "error"
                toast_message = "Invalid format provided inside production inputs."

        # HTMX interceptor configuration
        if request.headers.get('HX-Request'):
            response = render(request, 'livestock/dashboard_inner.html', get_livestock_context(today))
            response['X-Toast-Message'] = toast_message
            response['X-Toast-Status'] = toast_status
            return response

        return redirect('livestock:dashboard')

    return render(request, 'livestock/dashboard.html', get_livestock_context(today))


def get_livestock_context(today):
    """Encapsulates all KPI data matrices and empty Django form initializers"""
    active_groups = LivestockGroup.objects.filter(is_active=True)
    return {
        'active_groups': active_groups,
        'total_head_count': active_groups.aggregate(total=Sum('current_count'))['total'] or 0,
        'today_mortalities': DailyLog.objects.filter(date=today).aggregate(total=Sum('mortality'))['total'] or 0,
        'today_eggs': ProductionYield.objects.filter(date=today, yield_type='EGGS').aggregate(total=Sum('quantity_good'))['total'] or 0,
        'today_milk': ProductionYield.objects.filter(date=today, yield_type='MILK').aggregate(total=Sum('quantity_good'))['total'] or 0,
        
        'recent_logs': DailyLog.objects.all().order_by('-date', '-id')[:10],
        'recent_yields': ProductionYield.objects.all().order_by('-date', '-id')[:10],
        
        # Instantiate fresh Django forms into context area
        'batch_form': LivestockGroupForm(),
        'daily_form': DailyLogForm(),
        'yield_form': ProductionYieldForm(),
    }