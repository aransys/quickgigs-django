from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import TaskForm
from .models import Task


class TaskListView(ListView):
    model = Task
    template_name = "todo_app/task_list.html"
    context_object_name = "tasks"
    ordering = ["-created_at"]  # Show newest tasks first


class TaskDetailView(DetailView):
    model = Task
    template_name = "todo_app/task_detail.html"
    context_object_name = "task"


class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = "todo_app/task_form.html"
    success_url = reverse_lazy("todo_app:task_list")

    def form_valid(self, form):
        messages.success(self.request, "Task created successfully!")
        return super().form_valid(form)


class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "todo_app/task_form.html"
    success_url = reverse_lazy("todo_app:task_list")

    def form_valid(self, form):
        messages.success(self.request, "Task updated successfully!")
        return super().form_valid(form)


class TaskDeleteView(DeleteView):
    model = Task
    template_name = "todo_app/task_confirm_delete.html"
    success_url = reverse_lazy("todo_app:task_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Task deleted successfully!")
        return super().delete(request, *args, **kwargs)


# Function-based view for toggling task completion
def toggle_complete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.completed = not task.completed
    task.save()

    if task.completed:
        messages.success(request, f'Task "{task.title}" marked as complete!')
    else:
        messages.info(request, f'Task "{task.title}" marked as incomplete.')

    return redirect("todo_app:task_list")
