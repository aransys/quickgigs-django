from django.urls import path
from . import views

app_name = "gigs"  # Changed from "todo_app" to "gigs"

urlpatterns = [
    # ==================== TASK URLS (Todo App - Keep Working) ====================
    # List view - show all tasks
    path("tasks/", views.TaskListView.as_view(), name="task_list"),
    # Create view - add new task
    path("task/new/", views.TaskCreateView.as_view(), name="task_create"),
    # Detail view - show single task
    path("task/<int:pk>/", views.TaskDetailView.as_view(), name="task_detail"),
    # Update view - edit existing task
    path("task/<int:pk>/edit/", views.TaskUpdateView.as_view(), name="task_update"),
    # Delete view - remove task
    path("task/<int:pk>/delete/", views.TaskDeleteView.as_view(), name="task_delete"),
    # Toggle complete status
    path("task/<int:pk>/toggle/", views.toggle_complete, name="toggle_complete"),
    
    # ==================== GIG URLS (Job Board - New) ====================
    # Main page - show all gigs (this will be our new homepage)
    path("", views.GigListView.as_view(), name="gig_list"),
    # Create view - post new gig
    path("gig/post/", views.GigCreateView.as_view(), name="gig_create"),
    # Detail view - show single gig
    path("gig/<int:pk>/", views.GigDetailView.as_view(), name="gig_detail"),
    # Update view - edit existing gig
    path("gig/<int:pk>/edit/", views.GigUpdateView.as_view(), name="gig_update"),
    # Delete view - remove gig
    path("gig/<int:pk>/delete/", views.GigDeleteView.as_view(), name="gig_delete"),
    # Toggle gig active status
    path("gig/<int:pk>/toggle/", views.toggle_gig_status, name="toggle_gig_status"),
]