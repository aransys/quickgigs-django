from django.urls import path

from . import views

app_name = "todo_app"

urlpatterns = [
    # List view - show all tasks
    path("", views.TaskListView.as_view(), name="task_list"),
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
]
