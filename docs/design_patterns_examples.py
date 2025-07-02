# QuickGigs Design Patterns Implementation Examples
# This file demonstrates key design patterns used in the project

# ==============================================================================
# 1. MODEL-VIEW-TEMPLATE (MVT) PATTERN - Django's Core Architecture
# ==============================================================================

# MODEL: Business Logic and Data Access
class Gig(models.Model):
    """
    Model: Encapsulates business data and logic
    - Represents a freelance job posting
    - Contains validation and business rules
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    employer = models.ForeignKey(User, on_delete=models.CASCADE)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    
    def clean(self):
        """Business validation logic"""
        if self.budget <= 0:
            raise ValidationError("Budget must be positive")
    
    def is_available(self):
        """Business logic method"""
        return self.is_active and not self.is_expired()

# VIEW: Request/Response Logic
class GigCreateView(LoginRequiredMixin, CreateView):
    """
    View: Handles HTTP requests and responses
    - Separates presentation from business logic
    - Uses Django's CBV for consistency
    """
    model = Gig
    form_class = GigForm
    template_name = 'gigs/gig_form.html'
    
    def form_valid(self, form):
        form.instance.employer = self.request.user
        messages.success(self.request, 'Gig posted successfully!')
        return super().form_valid(form)

# TEMPLATE: Presentation Layer (in templates/gigs/gig_form.html)
"""
{% extends 'gigs/base.html' %}
{% block content %}
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Create Gig</button>
</form>
{% endblock %}
"""

# ==============================================================================
# 2. REPOSITORY PATTERN - Data Access Abstraction
# ==============================================================================

class GigRepository:
    """
    Repository Pattern: Encapsulates data access logic
    - Centralizes complex queries
    - Makes testing easier with mock repositories
    """
    
    @staticmethod
    def get_active_gigs_with_employers():
        """Optimized query with select_related"""
        return Gig.objects.select_related('employer').filter(
            is_active=True
        ).order_by('-is_featured', '-created_at')
    
    @staticmethod
    def get_featured_gigs(limit=3):
        """Business-specific query method"""
        return Gig.objects.filter(
            is_active=True, 
            is_featured=True
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def get_user_gigs(user):
        """User-specific data access"""
        return Gig.objects.filter(employer=user).prefetch_related('applications')

# Usage in Views
class GigListView(ListView):
    template_name = 'gigs/gig_list.html'
    
    def get_queryset(self):
        return GigRepository.get_active_gigs_with_employers()

# ==============================================================================
# 3. FACTORY PATTERN - Object Creation
# ==============================================================================

class PaymentFactory:
    """
    Factory Pattern: Creates different types of payments
    - Centralizes object creation logic
    - Easy to extend with new payment types
    """
    
    @staticmethod
    def create_featured_gig_payment(user, gig, stripe_payment_id):
        """Factory method for featured gig payments"""
        return Payment.objects.create(
            user=user,
            gig=gig,
            amount=9.99,
            stripe_payment_id=stripe_payment_id,
            payment_type='featured_gig',
            status='completed',
            description=f'Featured gig upgrade: {gig.title}'
        )
    
    @staticmethod
    def create_subscription_payment(user, subscription_type):
        """Factory method for subscription payments"""
        amounts = {
            'premium_profile': 19.99,
            'application_boost': 4.99
        }
        return Payment.objects.create(
            user=user,
            amount=amounts[subscription_type],
            payment_type=subscription_type,
            status='pending'
        )

# ==============================================================================
# 4. STRATEGY PATTERN - Algorithm Selection
# ==============================================================================

class PaymentProcessor:
    """
    Strategy Pattern: Different payment processing strategies
    - Allows switching payment providers
    - Encapsulates payment algorithms
    """
    
    def __init__(self, strategy):
        self.strategy = strategy
    
    def process_payment(self, amount, metadata):
        return self.strategy.process(amount, metadata)

class StripePaymentStrategy:
    """Concrete strategy for Stripe payments"""
    
    def process(self, amount, metadata):
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'gbp',
                    'unit_amount': int(amount * 100),
                    'product_data': {'name': metadata['product_name']}
                },
                'quantity': 1,
            }],
            mode='payment'
        )
        return session

class PayPalPaymentStrategy:
    """Future strategy for PayPal payments"""
    
    def process(self, amount, metadata):
        # PayPal implementation would go here
        pass

# Usage
def feature_gig_payment(request, gig_id):
    processor = PaymentProcessor(StripePaymentStrategy())
    session = processor.process_payment(9.99, {
        'product_name': f'Feature Gig: {gig.title}'
    })

# ==============================================================================
# 5. OBSERVER PATTERN - Event Handling
# ==============================================================================

# Django Signals implement Observer Pattern
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Observer Pattern: Automatic profile creation
    - Listens for User creation events
    - Automatically creates UserProfile
    """
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=Payment)
def update_gig_featured_status(sender, instance, created, **kwargs):
    """
    Observer Pattern: Payment completion handling
    - Listens for Payment status changes
    - Updates related gig status
    """
    if instance.status == 'completed' and instance.payment_type == 'featured_gig':
        if instance.gig:
            instance.gig.is_featured = True
            instance.gig.save()

# ==============================================================================
# 6. DECORATOR PATTERN - Functionality Extension
# ==============================================================================

def ownership_required(view_func):
    """
    Decorator Pattern: Adds ownership verification
    - Extends view functionality
    - Reusable across multiple views
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        gig = get_object_or_404(Gig, pk=kwargs['pk'])
        if request.user != gig.employer:
            messages.error(request, 'You can only manage your own gigs.')
            return redirect('gigs:gig_list')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@ownership_required
def toggle_gig_status(request, pk):
    """Usage of ownership decorator"""
    gig = get_object_or_404(Gig, pk=pk)
    gig.is_active = not gig.is_active
    gig.save()
    return redirect('gigs:gig_detail', pk=pk)

# ==============================================================================
# 7. COMMAND PATTERN - Encapsulating Requests
# ==============================================================================

class GigCommand:
    """
    Command Pattern: Encapsulates gig operations
    - Allows undo/redo functionality
    - Queuing and logging of operations
    """
    
    def execute(self):
        raise NotImplementedError
    
    def undo(self):
        raise NotImplementedError

class CreateGigCommand(GigCommand):
    """Concrete command for gig creation"""
    
    def __init__(self, gig_data, employer):
        self.gig_data = gig_data
        self.employer = employer
        self.created_gig = None
    
    def execute(self):
        self.created_gig = Gig.objects.create(
            employer=self.employer,
            **self.gig_data
        )
        return self.created_gig
    
    def undo(self):
        if self.created_gig:
            self.created_gig.delete()

class FeatureGigCommand(GigCommand):
    """Concrete command for featuring gigs"""
    
    def __init__(self, gig):
        self.gig = gig
        self.was_featured = gig.is_featured
    
    def execute(self):
        self.gig.is_featured = True
        self.gig.save()
    
    def undo(self):
        self.gig.is_featured = self.was_featured
        self.gig.save()

# Command Invoker
class GigManager:
    """Invoker class that executes commands"""
    
    def __init__(self):
        self.command_history = []
    
    def execute_command(self, command):
        result = command.execute()
        self.command_history.append(command)
        return result
    
    def undo_last_command(self):
        if self.command_history:
            command = self.command_history.pop()
            command.undo()

# ==============================================================================
# 8. TEMPLATE METHOD PATTERN - Algorithm Skeleton
# ==============================================================================

class BasePaymentView(View):
    """
    Template Method Pattern: Defines payment processing skeleton
    - Subclasses implement specific steps
    - Ensures consistent payment flow
    """
    
    def post(self, request, *args, **kwargs):
        """Template method defining the payment process"""
        if not self.validate_user():
            return self.handle_invalid_user()
        
        payment_data = self.prepare_payment_data()
        
        try:
            payment_session = self.create_payment_session(payment_data)
            self.log_payment_attempt(payment_data)
            return self.handle_success(payment_session)
        except Exception as e:
            return self.handle_error(e)
    
    # Abstract methods for subclasses to implement
    def validate_user(self):
        raise NotImplementedError
    
    def prepare_payment_data(self):
        raise NotImplementedError
    
    def create_payment_session(self, payment_data):
        raise NotImplementedError

class FeatureGigPaymentView(BasePaymentView):
    """Concrete implementation for gig featuring"""
    
    def validate_user(self):
        gig = get_object_or_404(Gig, pk=self.kwargs['gig_id'])
        return self.request.user == gig.employer
    
    def prepare_payment_data(self):
        gig = get_object_or_404(Gig, pk=self.kwargs['gig_id'])
        return {
            'amount': 9.99,
            'gig': gig,
            'user': self.request.user
        }

# ==============================================================================
# SUMMARY: Design Patterns Benefits in QuickGigs
# ==============================================================================

"""
1. MVT Pattern: Clear separation of concerns, maintainable code structure
2. Repository Pattern: Centralized data access, easier testing and optimization
3. Factory Pattern: Flexible object creation, easy to extend payment types
4. Strategy Pattern: Pluggable payment processors, algorithm flexibility
5. Observer Pattern: Automatic profile creation, event-driven architecture
6. Decorator Pattern: Reusable functionality, clean security implementation
7. Command Pattern: Encapsulated operations, potential for undo/redo
8. Template Method: Consistent payment flows, extensible process definitions

These patterns make QuickGigs more maintainable, testable, and extensible.
""" 