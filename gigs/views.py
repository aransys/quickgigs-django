from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
# from .forms import TaskForm  # We'll create GigForm next
# from .models import Task, Gig
from .models import Gig
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# ==================== EXISTING TASK VIEWS (Keep working) ====================

# class TaskListView(ListView):
#     model = Task
#     template_name = "gigs/task_list.html"  # Updated path
#     context_object_name = "tasks"
#     ordering = ["-created_at"]

# class TaskDetailView(DetailView):
#     model = Task
#     template_name = "gigs/task_detail.html"  # Updated path
#     context_object_name = "task"

# class TaskCreateView(CreateView):
#     model = Task
#     form_class = TaskForm
#     template_name = "gigs/task_form.html"  # Updated path
#     success_url = reverse_lazy("gigs:task_list")  # Updated namespace

#     def form_valid(self, form):
#         messages.success(self.request, "Task created successfully!")
#         return super().form_valid(form)

# class TaskUpdateView(UpdateView):
#     model = Task
#     form_class = TaskForm
#     template_name = "gigs/task_form.html"  # Updated path
#     success_url = reverse_lazy("gigs:task_list")  # Updated namespace

#     def form_valid(self, form):
#         messages.success(self.request, "Task updated successfully!")
#         return super().form_valid(form)

# class TaskDeleteView(DeleteView):
#     model = Task
#     template_name = "gigs/task_confirm_delete.html"  # Updated path
#     success_url = reverse_lazy("gigs:task_list")  # Updated namespace

#     def delete(self, request, *args, **kwargs):
#         messages.success(self.request, "Task deleted successfully!")
#         return super().delete(request, *args, **kwargs)

# def toggle_complete(request, pk):
#     task = get_object_or_404(Task, pk=pk)
#     task.completed = not task.completed
#     task.save()
#     if task.completed:
#         messages.success(request, f'Task "{task.title}" marked as complete!')
#     else:
#         messages.info(request, f'Task "{task.title}" marked as incomplete.')
#     return redirect("gigs:task_list")  # Updated namespace

# ==================== NEW GIG VIEWS (Job Board) ====================

class GigListView(ListView):
    model = Gig
    template_name = "gigs/gig_list.html"
    context_object_name = "gigs"
    ordering = ["-is_featured", "-created_at"]  # Featured first, then newest
    paginate_by = 12  # Add pagination for better performance

    def get_queryset(self):
        # Only show active gigs with employer data (prevents N+1 queries)
        return Gig.objects.select_related('employer').filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add statistics for the template
        context['featured_count'] = Gig.objects.filter(is_featured=True, is_active=True).count()
        context['employers_count'] = User.objects.filter(posted_gigs__is_active=True).distinct().count()
        return context

class GigDetailView(DetailView):
    model = Gig
    template_name = "gigs/gig_detail.html"
    context_object_name = "gig"
    
    def get_queryset(self):
        # Optimize employer data fetching
        return Gig.objects.select_related('employer')

class GigCreateView(LoginRequiredMixin, CreateView):
    model = Gig
    fields = ['title', 'description', 'budget', 'location', 'category', 'deadline']
    template_name = "gigs/gig_form.html"
    success_url = reverse_lazy("gigs:gig_list")

    def form_valid(self, form):
        # Automatically set the employer to the current user
        form.instance.employer = self.request.user
        messages.success(self.request, "Gig posted successfully!")
        return super().form_valid(form)

class GigUpdateView(LoginRequiredMixin, UpdateView):
    model = Gig
    fields = ['title', 'description', 'budget', 'location', 'category', 'deadline', 'is_active']
    template_name = "gigs/gig_form.html"
    success_url = reverse_lazy("gigs:gig_list")

    def get_queryset(self):
        # Only allow employers to edit their own gigs (with optimization)
        return Gig.objects.select_related('employer').filter(employer=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Gig updated successfully!")
        return super().form_valid(form)

class GigDeleteView(LoginRequiredMixin, DeleteView):
    model = Gig
    template_name = "gigs/gig_confirm_delete.html"
    success_url = reverse_lazy("gigs:gig_list")

    def get_queryset(self):
        # Only allow employers to delete their own gigs (with optimization)
        return Gig.objects.select_related('employer').filter(employer=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Gig deleted successfully!")
        return super().delete(request, *args, **kwargs)
    
@login_required
def toggle_gig_status(request, pk):
    """Toggle gig between active and inactive"""
    # Optimized: Use select_related for consistency (though not critical here since it's just one gig)
    gig = get_object_or_404(
        Gig.objects.select_related('employer'), 
        pk=pk, 
        employer=request.user
    )
    gig.is_active = not gig.is_active
    gig.save()
    
    if gig.is_active:
        messages.success(request, f'Gig "{gig.title}" is now active!')
    else:
        messages.info(request, f'Gig "{gig.title}" is now inactive.')
    
    return redirect("gigs:gig_list")