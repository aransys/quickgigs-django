import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from gigs.models import Gig
from .models import Payment

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def feature_gig_checkout(request, gig_id):
    """Create Stripe checkout session for featuring a gig"""
    gig = get_object_or_404(Gig, id=gig_id, employer=request.user)
    
    if gig.is_featured:
        messages.warning(request, "This gig is already featured!")
        return redirect('gigs:gig_detail', pk=gig.id)
    
    try:
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Feature Gig: {gig.title}',
                        'description': 'Make your gig stand out with featured placement',
                    },
                    'unit_amount': int(settings.FEATURED_GIG_PRICE * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(
                reverse('payments:payment_success', kwargs={'gig_id': gig.id})
            ),
            cancel_url=request.build_absolute_uri(
                reverse('payments:payment_cancel', kwargs={'gig_id': gig.id})
            ),
            metadata={
                'gig_id': gig.id,
                'user_id': request.user.id,
                'payment_type': 'featured_gig'
            }
        )
        
        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            gig=gig,
            amount=settings.FEATURED_GIG_PRICE,
            payment_type='featured_gig',
            status='pending',
            stripe_payment_id=checkout_session.id,
            description=f'Feature gig: {gig.title}'
        )
        
        return redirect(checkout_session.url, code=303)
        
    except Exception as e:
        messages.error(request, f"Error creating payment session: {str(e)}")
        return redirect('gigs:gig_detail', pk=gig.id)

def payment_success(request, gig_id):
    """Handle successful payment"""
    gig = get_object_or_404(Gig, id=gig_id)
    
    # Mark gig as featured
    gig.is_featured = True
    gig.save()
    
    # Update payment status
    try:
        payment = Payment.objects.filter(
            gig=gig,
            payment_type='featured_gig',
            status='pending'
        ).latest('created_at')
        payment.status = 'completed'
        payment.save()
    except Payment.DoesNotExist:
        pass
    
    messages.success(
        request, 
        f'🎉 Payment successful! "{gig.title}" is now featured and will appear at the top of listings.'
    )
    
    return render(request, 'payments/success.html', {'gig': gig})

def payment_cancel(request, gig_id):
    """Handle cancelled payment"""
    gig = get_object_or_404(Gig, id=gig_id)
    
    # Update payment status to failed
    try:
        payment = Payment.objects.filter(
            gig=gig,
            payment_type='featured_gig',
            status='pending'
        ).latest('created_at')
        payment.status = 'failed'
        payment.save()
    except Payment.DoesNotExist:
        pass
    
    messages.info(request, 'Payment was cancelled. Your gig remains active but not featured.')
    
    return render(request, 'payments/cancel.html', {'gig': gig})

@login_required
def payment_history(request):
    """Display user's payment history"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'payments': payments
    }
    
    return render(request, 'payments/history.html', context)

@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhooks (optional but recommended for production)"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Handle successful payment
        # This would be more robust payment confirmation
        pass
    
    return JsonResponse({'status': 'success'})