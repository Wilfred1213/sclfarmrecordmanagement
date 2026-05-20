from django.shortcuts import render, redirect
from django.utils import timezone
from sclApp.medical.models import StaffMedicalCase, StaffTreatmentLog
from sclApp.medical.forms import StaffMedicalCaseForm, StaffTreatmentLogForm
def staff_medical_dashboard(request):
    toast_message = ""
    toast_status = "success"
    today = timezone.now().date()

    if request.method == 'POST':
        if 'open_case' in request.POST:
            form = StaffMedicalCaseForm(request.POST)
            if form.is_valid():
                new_case = form.save()
                toast_message = f"Medical file opened for {new_case.staff_member.get_full_name() or new_case.staff_member.username}."
            else:
                toast_status = "error"
                toast_message = "Form validation failed. Please review worker details."

        elif 'log_treatment' in request.POST:
            form = StaffTreatmentLogForm(request.POST)
            if form.is_valid():
                treatment = form.save()
                toast_message = f"Treatment logs updated by {treatment.administered_by}."
            else:
                toast_status = "error"
                toast_message = "Failed to submit clinical treatment row."

        if request.headers.get('HX-Request'):
            response = render(request, 'medical/staff_medical_inner.html', get_staff_medical_context(today))
            response['X-Toast-Message'] = toast_message
            response['X-Toast-Status'] = toast_status
            return response

        return redirect('medical:staff_medical')

    return render(request, 'medical/medical_center.html', get_staff_medical_context(today))


def get_staff_medical_context(today):
    all_cases = StaffMedicalCase.objects.all().order_by('-incident_date')
    return {
        'cases': all_cases,
        'active_incidents_count': all_cases.exclude(status='RESOLVED').count(),
        'on_sick_leave_count': all_cases.filter(status='SICK_LEAVE').count(),
        'recent_treatments': StaffTreatmentLog.objects.all().order_by('-treatment_date')[:10],
        'case_form': StaffMedicalCaseForm(),
        'treatment_form': StaffTreatmentLogForm(),
    }