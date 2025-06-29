from django.urls import path
from . import views

app_name = 'gigs'

urlpatterns = [
    # Main gig listings
    path('', views.GigListView.as_view(), name='gig_list'),
    path('post/', views.GigCreateView.as_view(), name='gig_create'),
    path('<int:pk>/', views.GigDetailView.as_view(), name='gig_detail'),
    path('<int:pk>/edit/', views.GigUpdateView.as_view(), name='gig_update'),
    path('<int:pk>/delete/', views.GigDeleteView.as_view(), name='gig_delete'),
    path('<int:pk>/toggle/', views.toggle_gig_status, name='toggle_gig_status'),
    
    # Task URLs (removed)
    # path('tasks/', views.TaskListView.as_view(), name='task_list'),
    # path('task/new/', views.TaskCreateView.as_view(), name='task_create'),
    # path('task/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    # path('task/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_update'),
    # path('task/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    # path('task/<int:pk>/toggle/', views.toggle_complete, name='toggle_complete'),

    # Application URLs
    path('<int:pk>/apply/', views.apply_to_gig, name='apply_to_gig'),
    path('<int:pk>/applications/', views.gig_applications, name='gig_applications'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('my-gigs/', views.my_gigs, name='my_gigs'),
    path('application/<int:pk>/', views.ApplicationDetailView.as_view(), name='application_detail'),
    path('application/<int:pk>/update-status/', views.update_application_status, name='update_application_status'),
    path('application/<int:pk>/withdraw/', views.withdraw_application, name='withdraw_application'),
]