from django.shortcuts import render
from django.views.generic import TemplateView
from gigs.models import Gig
from accounts.models import UserProfile

class HomeView(TemplateView):
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get recent active gigs for homepage
        context['recent_gigs'] = Gig.objects.filter(is_active=True).order_by('-created_at')[:6]
        # Get featured gigs
        context['featured_gigs'] = Gig.objects.filter(is_featured=True, is_active=True).order_by('-created_at')[:3]
        # Platform statistics
        context['total_gigs'] = Gig.objects.filter(is_active=True).count()
        context['total_employers'] = UserProfile.objects.filter(user_type='employer').count()
        context['total_freelancers'] = UserProfile.objects.filter(user_type='freelancer').count()
        return context

class AboutView(TemplateView):
    template_name = 'core/about.html'

class ContactView(TemplateView):
    template_name = 'core/contact.html'