from django.contrib import admin
from .models import Person, Attendance, AttendanceRule


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'employee_id', 'created_at']


@admin.register(AttendanceRule)
class AttendanceRuleAdmin(admin.ModelAdmin):
    list_display = ['checkin_deadline', 'allow_repeat', 'updated_at']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['person', 'check_in_time', 'status', 'source']
    list_filter = ['check_in_time', 'status']
