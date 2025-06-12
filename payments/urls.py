from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Feature gig payment flow
    path('feature-gig/<int:gig_id>/', views.feature_gig_checkout, name='feature_gig_checkout'),
    path('success/<int:gig_id>/', views.payment_success, name='payment_success'),
    path('cancel/<int:gig_id>/', views.payment_cancel, name='payment_cancel'),
    
    # Payment history
    path('history/', views.payment_history, name='payment_history'),
    
    # Stripe webhook
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]