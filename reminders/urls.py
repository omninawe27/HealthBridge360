from django.urls import path
from . import views

app_name = 'reminders'

urlpatterns = [
    path('', views.reminder_list, name='list'),
    path('add/', views.add_reminder, name='add'),
    path('edit/<int:reminder_id>/', views.edit_reminder, name='edit'),
    path('delete/<int:reminder_id>/', views.delete_reminder, name='delete'),
    path('toggle/<int:reminder_id>/', views.toggle_reminder, name='toggle'),
    path('toggle-ajax/<int:reminder_id>/', views.toggle_reminder_ajax, name='toggle_ajax'),
    path('add-ajax/', views.add_reminder_ajax, name='add_ajax'),
    path('due-reminders/', views.get_due_reminders, name='due_reminders'),
    path('mark-taken/<int:reminder_id>/', views.toggle_reminder_taken, name='mark_taken'),
    path('statistics/', views.reminder_statistics, name='statistics'),
    path('bulk-actions/', views.bulk_actions, name='bulk_actions'),
    path('test-notification/<int:reminder_id>/', views.test_notification, name='test_notification'),
]
