from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ProductionArea, CropBatch, SprayingLog, HarvestLog, DailyActivityLog
from .forms import CropBatchForm, SprayingLogForm, HarvestLogForm, DailyActivityLogForm

@login_required
def greenhouse_dashboard(request):
    # Base queries for data display
    active_batches = CropBatch.objects.filter(is_harvested=False).select_related('location')
    recent_sprays = SprayingLog.objects.all().select_related('batch__location').order_by('-date_applied')[:10]
    recent_harvests = HarvestLog.objects.all().select_related('batch__location').order_by('-date_harvested')[:5]
    recent_activities = DailyActivityLog.objects.all().select_related('batch__location', 'logged_by').order_by('-id')[:15]

    if request.method == 'POST':
        # ---------------------------------------------------------------------
        # CASE 1: HARVEST FORM SUBMISSION
        # ---------------------------------------------------------------------
        if 'submit_harvest' in request.POST:
            harvest_form = HarvestLogForm(request.POST)
            if harvest_form.is_valid():
                harvest = harvest_form.save(commit=False)
                harvest.logged_by = request.user
                harvest.save()

        # ---------------------------------------------------------------------
        # CASE 2: TRANSPLANT LOG FORM SUBMISSION
        # ---------------------------------------------------------------------
        elif 'submit_crop' in request.POST:
            crop_form = CropBatchForm(request.POST)
            if crop_form.is_valid():
                crop_form.save()

        # ---------------------------------------------------------------------
        # CASE 3: RECORD IPM SPRAY FORM SUBMISSION
        # ---------------------------------------------------------------------
        elif 'submit_spray' in request.POST:
            spray_form = SprayingLogForm(request.POST)
            if spray_form.is_valid():
                spray_form.save()

        # ---------------------------------------------------------------------
        # CASE 4: DAILY MAINTENANCE & SCOOPING ACTIVITY LOG
        # ---------------------------------------------------------------------
        elif 'submit_activity' in request.POST:
            activity_form = DailyActivityLogForm(request.POST)
            if activity_form.is_valid():
                activity = activity_form.save(commit=False)
                activity.logged_by = request.user
                activity.save()

        # ---------------------------------------------------------------------
        # THE UNIFIED HTMX RESPONSE ROUTER
        # ---------------------------------------------------------------------
        # If any of the submissions above came from HTMX, instantly intercept here
        if request.headers.get('HX-Request'):
            # Re-fetch fresh arrays so progress bars and data tables have updated math
            active_batches = CropBatch.objects.filter(is_harvested=False).select_related('location')
            recent_harvests = HarvestLog.objects.all().select_related('batch__location').order_by('-date_harvested')[:5]
            recent_sprays = SprayingLog.objects.all().select_related('batch__location').order_by('-date_applied')[:10]
            recent_activities = DailyActivityLog.objects.all().select_related('batch__location', 'logged_by').order_by('-id')[:15]
            
            context = {
                'active_batches': active_batches,
                'recent_harvests': recent_harvests,
                'recent_sprays': recent_sprays,
                'recent_activities': recent_activities,
                'crop_form': CropBatchForm(),
                'spray_form': SprayingLogForm(),
                # 'area_form': ProductionAreaForm(),
                'harvest_form': HarvestLogForm(),
                'activity_form': DailyActivityLogForm(),
            }
            # Initialize the base template rendering response
            response = render(request, 'greenhouse/dashboard.html', context)
            
            # DYNAMICALLY DETERMINE NOTIFICATION MESSAGE BASED ON SUBMITTED HIDDEN INPUT
            if 'submit_harvest' in request.POST:
                response['X-Toast-Message'] = "Harvest log updated successfully!"
                response['X-Toast-Status'] = "success"
            elif 'submit_crop' in request.POST:
                response['X-Toast-Message'] = "New active crop cycle launched successfully!"
                response['X-Toast-Status'] = "success"
            elif 'submit_spray' in request.POST:
                response['X-Toast-Message'] = "IPM Treatment recorded in system logs."
                response['X-Toast-Status'] = "success"
            elif 'submit_activity' in request.POST:
                response['X-Toast-Message'] = "Daily field activity recorded."
                response['X-Toast-Status'] = "success"
            else:
                response['X-Toast-Message'] = "Record updated successfully."
                response['X-Toast-Status'] = "success"
                
            return response
            # return render(request, 'greenhouse/dashboard.html', context)

        # Fallback standard page reload if JavaScript/HTMX fails on an old phone
        return redirect('greenhouse:greehouse_dashboard')

    crop_form = CropBatchForm()
    spray_form = SprayingLogForm()
    harvest_form = HarvestLogForm()
    activity_form = DailyActivityLogForm()

    context = {
        'active_batches': active_batches,
        'recent_sprays': recent_sprays,
        'recent_harvests': recent_harvests,
        'recent_activities': recent_activities,
        'crop_form': crop_form,
        'spray_form': spray_form,
        'harvest_form': harvest_form,
        'activity_form': activity_form,
    }
    
    return render(request, 'greenhouse/dashboard.html', context)
# @login_required
# def greenhouse_dashboard(request):
#     # Fetch data to present on the dashboard
#     active_batches = CropBatch.objects.filter(is_harvested=False).select_related('location')
#     recent_sprays = SprayingLog.objects.all().select_related('batch__location').order_by('-date_applied')[:10]
#     recent_harvests = HarvestLog.objects.all().select_related('batch__location').order_by('-date_harvested')[:5]
#     # NEW: Fetch the last 15 daily operations activities
#     recent_activities = DailyActivityLog.objects.all().select_related('batch__location', 'logged_by').order_by('-id')[:15]

#     # Process Form Submissions
#     if request.method == 'POST':
        
#         # ---------------------------------------------------------------------
#         # CASE 1: INITIALIZE NEW CROP BATCH FORM
#         # ---------------------------------------------------------------------
#         if 'submit_crop' in request.POST:
#             crop_form = CropBatchForm(request.POST)
#             if crop_form.is_valid():
#                 batch = crop_form.save()
#                 messages.success(
#                     request, 
#                     f"Success: Initialized {batch.plant_count} seedlings of {batch.variety} ({batch.get_crop_type_display()}) at {batch.location}."
#                 )
#                 return redirect('greenhouse:greenhouse_dashboard')
#             else:
#                 messages.error(request, "Failed to log transplant. Please verify form inputs.")
                

#         # ---------------------------------------------------------------------
#         # CASE 2: RECORD ORGANIC IPM SPRAY APPLICATION FORM
#         # ---------------------------------------------------------------------
#         elif 'submit_spray' in request.POST:
#             spray_form = SprayingLogForm(request.POST)
#             if spray_form.is_valid():
#                 log = spray_form.save(commit=False)
                
#                 # Attach the logged-in custom user model agent automatically
#                 log.operator = request.user
#                 log.save()
                
#                 # Use contextual color-coded messaging for active curative operations
#                 if log.application_type == 'CURA':
#                     messages.warning(
#                         request, 
#                         f"IPM Alert: Curative treatment of {log.remedy_used} logged for {log.batch.location} against {log.target_pest_disease}."
#                     )
#                 else:
#                     messages.success(
#                         request, 
#                         f"IPM Success: Preventative spray of {log.remedy_used} completed across {log.batch.location}."
#                     )
#                 return redirect('greenhouse:greenhouse_dashboard')
#             else:
#                 messages.error(request, "Failed to record spray log entry. Check input parameters.")
        
#         # ---------------------------------------------------------------------
#         # NEW CASE: RECORD HARVEST FORM SUBMISSION
#         # ---------------------------------------------------------------------
#         elif 'submit_harvest' in request.POST or request.headers.get('HX-Request'):
#             harvest_form = HarvestLogForm(request.POST)
#             if harvest_form.is_valid():
#                 harvest = harvest_form.save(commit=False)
#                 harvest.logged_by = request.user
#                 harvest.save()
                
#                 # If it's an HTMX request, return ONLY the updated tables fragment directly
#                 if request.headers.get('HX-Request'):
#                     context = {
#                         'active_batches': active_batches,
#                         'recent_harvests': recent_harvests,
#                         'recent_sprays': recent_sprays,
#                         'recent_activities': recent_activities,
#                     }
#                     # Returns just the updated tables block instantly!
#                     # return render(request, 'greenhouse/partials/dashboard_tables.html', context)
#                     return redirect('greenhouse:greenhouse_dashboard')
                
#                 messages.success(request, "Harvest Logged Successfully.")
#                 return redirect('greenhouse:greenhouse_dashboard')
        
#         # ---------------------------------------------------------------------
#         # NEW CASE: RECORD DAILY ACTIVITY LOG
#         # ---------------------------------------------------------------------
#         elif 'submit_activity' in request.POST:
#             activity_form = DailyActivityLogForm(request.POST)
#             if activity_form.is_valid():
#                 activity = activity_form.save(commit=False)
#                 activity.logged_by = request.user
#                 activity.save()
#                 messages.success(request, f"Activity Logged: Recorded {activity.get_activity_type_display()} for {activity.batch.location}.")
#                 return redirect('greenhouse:greenhouse_dashboard')
#             else:
#                 messages.error(request, "Failed to log activity. Verify your details.")

#         # ... keep your other 'submit_area', 'submit_crop', and 'submit_spray' blocks intact ...
#     # GET Request initialization or fallback
#     crop_form = CropBatchForm()
#     spray_form = SprayingLogForm()
#     harvest_form = HarvestLogForm()
#     activity_form = DailyActivityLogForm()

#     context = {
#         'active_batches': active_batches,
#         'recent_sprays': recent_sprays,
#         'recent_harvests': recent_harvests,
#         'recent_activities': recent_activities,
#         'crop_form': crop_form,
#         'spray_form': spray_form,
#         'harvest_form': harvest_form,
#         'activity_form': activity_form,
#     }
    
#     return render(request, 'greenhouse/dashboard.html', context)