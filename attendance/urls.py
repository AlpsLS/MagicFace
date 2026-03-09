from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('enrollment/', views.enrollment, name='enrollment'),
    path('enrollment/upload/', views.enrollment_upload, name='enrollment_upload'),
    path('checkin/', views.checkin, name='checkin'),
    path('checkin/submit/', views.checkin_submit, name='checkin_submit'),
    path('checkin/frame/', views.checkin_frame, name='checkin_frame'),
    path('report/', views.report, name='report'),
    path('api/attendance/stats/', views.attendance_stats, name='attendance_stats'),
    path('api/attendance/detail/', views.attendance_detail, name='attendance_detail'),
]
