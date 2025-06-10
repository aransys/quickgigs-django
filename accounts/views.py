from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from .models import UserProfile
from .forms import SignUpForm, UserProfileForm

class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('accounts:choose_role')
    template_name = 'accounts/signup.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)  # Auto login after signup
        messages.success(self.request, f"Welcome to QuickGigs, {self.object.username}!")
        return response

@login_required
def choose_role(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        if role in ['employer', 'freelancer']:
            profile = request.user.userprofile
            profile.user_type = role
            profile.save()
            
            if role == 'employer':
                messages.success(request, "Great! You're set up as an employer. Start posting gigs!")
            else:
                messages.success(request, "Perfect! You're set up as a freelancer. Start browsing gigs!")
            
            return redirect('gigs:gig_list')
    
    return render(request, 'accounts/choose_role.html')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

class ProfileUpdateView(UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user.userprofile
    
    def form_valid(self, form):
        messages.success(self.request, "Your profile has been updated successfully!")
        return super().form_valid(form)