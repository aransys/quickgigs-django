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
]