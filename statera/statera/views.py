from django.shortcuts import render

from .models import Employee, TimeEntry

def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'employee_list.html', {'employees': employees})

def time_entry_list(request):
    time_entries = TimeEntry.objects.all()
    return render(request, 'time_entry_list.html', {'time_entries': time_entries})

def home(request):
    return render(request, 'home.html')  # Point to a template