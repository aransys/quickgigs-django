from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
# from .forms import TaskForm  # We'll create GigForm next
# from .models import Task, Gig
from .models import Gig, Application
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import Http404
from .forms import GigForm, ApplicationForm, ApplicationStatusForm

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
    paginate_by = 12

    def get_queryset(self):
        queryset = Gig.objects.filter(is_active=True).select_related('employer')
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Gig.CATEGORY_CHOICES
        context['current_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context

class GigDetailView(DetailView):
    model = Gig
    template_name = "gigs/gig_detail.html"
    context_object_name = "gig"
    
    def get_queryset(self):
        # Optimize employer data fetching
        return Gig.objects.select_related('employer')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if user has already applied
        if self.request.user.is_authenticated:
            context['user_application'] = Application.objects.filter(
                gig=self.object,
                applicant=self.request.user
            ).first()
            
        # Get application count for employer
        if self.request.user == self.object.employer:
            context['application_count'] = self.object.applications.count()
            
        return context

class GigCreateView(LoginRequiredMixin, CreateView):
    model = Gig
    form_class = GigForm
    template_name = "gigs/gig_form.html"
    success_url = reverse_lazy("gigs:gig_list")

    def form_valid(self, form):
        # Automatically set the employer to the current user
        form.instance.employer = self.request.user
        messages.success(self.request, "Gig posted successfully! You can manage it from your 'My Gigs' page.")
        return super().form_valid(form)

class GigUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Gig
    form_class = GigForm
    template_name = "gigs/gig_form.html"
    success_url = reverse_lazy("gigs:gig_list")

    def test_func(self):
        gig = self.get_object()
        return self.request.user == gig.employer

    def form_valid(self, form):
        messages.success(self.request, "Gig updated successfully!")
        return super().form_valid(form)

class GigDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Gig
    template_name = "gigs/gig_confirm_delete.html"
    success_url = reverse_lazy("gigs:gig_list")

    def test_func(self):
        gig = self.get_object()
        return self.request.user == gig.employer

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Gig deleted successfully!")
        return super().delete(request, *args, **kwargs)
    
@login_required
def toggle_gig_status(request, pk):
    gig = get_object_or_404(Gig, pk=pk)
    
    if request.user != gig.employer:
        messages.error(request, 'You can only manage your own gigs.')
        return redirect('gigs:gig_detail', pk=pk)
    
    gig.is_active = not gig.is_active
    gig.save()
    
    status = "activated" if gig.is_active else "deactivated"
    messages.success(request, f'Your gig has been {status}.')
    
    return redirect('gigs:gig_detail', pk=pk)

# Application Views
@login_required
def apply_to_gig(request, pk):
    gig = get_object_or_404(Gig, pk=pk)
    
    # Check if user is the employer
    if request.user == gig.employer:
        messages.error(request, "You cannot apply to your own gig.")
        return redirect('gigs:gig_detail', pk=pk)
    
    # Check if user has already applied
    existing_application = Application.objects.filter(gig=gig, applicant=request.user).first()
    if existing_application:
        messages.info(request, "You have already applied to this gig.")
        return redirect('gigs:gig_detail', pk=pk)
    
    # Check if gig is active
    if not gig.is_active:
        messages.error(request, "This gig is no longer accepting applications.")
        return redirect('gigs:gig_detail', pk=pk)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.gig = gig
            application.applicant = request.user
            application.save()
            
            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('gigs:gig_detail', pk=pk)
    else:
        form = ApplicationForm()
    
    context = {
        'form': form,
        'gig': gig,
    }
    return render(request, 'gigs/apply_to_gig.html', context)

class ApplicationDetailView(LoginRequiredMixin, DetailView):
    model = Application
    template_name = 'gigs/application_detail.html'
    context_object_name = 'application'

    def get_object(self):
        application = get_object_or_404(Application, pk=self.kwargs['pk'])
        
        # Only allow applicant or employer to view
        if self.request.user not in [application.applicant, application.gig.employer]:
            raise Http404("Application not found")
            
        return application

@login_required
def my_applications(request):
    applications = Application.objects.filter(
        applicant=request.user
    ).select_related('gig', 'gig__employer').order_by('-created_at')
    
    context = {
        'applications': applications,
    }
    return render(request, 'gigs/my_applications.html', context)

@login_required
def my_gigs(request):
    """View for employers to see all their posted gigs"""
    gigs = Gig.objects.filter(
        employer=request.user
    ).prefetch_related('applications').order_by('-created_at')
    
    # Calculate summary statistics
    total_gigs = gigs.count()
    active_gigs = gigs.filter(is_active=True).count()
    total_applications = sum(gig.applications.count() for gig in gigs)
    pending_applications = sum(gig.applications.filter(status='pending').count() for gig in gigs)
    
    # Add application counts to each gig
    for gig in gigs:
        gig.application_count = gig.applications.count()
        gig.pending_applications = gig.applications.filter(status='pending').count()
    
    context = {
        'gigs': gigs,
        'total_gigs': total_gigs,
        'active_gigs': active_gigs,
        'total_applications': total_applications,
        'pending_applications': pending_applications,
    }
    return render(request, 'gigs/my_gigs.html', context)

@login_required
def gig_applications(request, pk):
    gig = get_object_or_404(Gig, pk=pk)
    
    # Only employer can view applications
    if request.user != gig.employer:
        messages.error(request, "You can only view applications for your own gigs.")
        return redirect('gigs:gig_detail', pk=pk)
    
    applications = gig.applications.select_related('applicant').order_by('-created_at')
    
    context = {
        'gig': gig,
        'applications': applications,
    }
    return render(request, 'gigs/gig_applications.html', context)

@login_required
def update_application_status(request, pk):
    application = get_object_or_404(Application, pk=pk)
    
    # Only employer can update status
    if request.user != application.gig.employer:
        messages.error(request, "You can only manage applications for your own gigs.")
        return redirect('gigs:gig_detail', pk=application.gig.pk)
    
    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, 'Application status updated successfully!')
            return redirect('gigs:gig_applications', pk=application.gig.pk)
    else:
        form = ApplicationStatusForm(instance=application)
    
    context = {
        'form': form,
        'application': application,
    }
    return render(request, 'gigs/update_application_status.html', context)

@login_required
def withdraw_application(request, pk):
    application = get_object_or_404(Application, pk=pk)
    
    # Only applicant can withdraw
    if request.user != application.applicant:
        messages.error(request, "You can only withdraw your own applications.")
        return redirect('gigs:gig_detail', pk=application.gig.pk)
    
    # Can only withdraw pending applications
    if application.status != 'pending':
        messages.error(request, "You can only withdraw pending applications.")
        return redirect('gigs:my_applications')
    
    if request.method == 'POST':
        application.status = 'withdrawn'
        application.save()
        messages.success(request, 'Application withdrawn successfully.')
        return redirect('gigs:my_applications')
    
    context = {
        'application': application,
    }
    return render(request, 'gigs/withdraw_application.html', context)