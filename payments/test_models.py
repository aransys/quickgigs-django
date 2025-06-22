import uuid
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from gigs.models import Gig
from .models import Payment, PaymentHistory

class PaymentModelTest(TestCase):
    def setUp(self):
        """Create test user and gig for payment tests"""
        self.user = User.objects.create_user(
            username='testemployer',
            email='test@example.com',
            password='testpass123'
        )
        
        self.gig = Gig.objects.create(
            title='Test Gig',
            description='Test description',
            employer=self.user,
            budget=Decimal('100.00'),
            category='web_development'
        )
    
    def create_unique_payment(self, **overrides):
        """Helper method to create payments with unique stripe_payment_id"""
        defaults = {
            'user': self.user,
            'gig': self.gig,
            'amount': Decimal('9.99'),
            'payment_type': 'featured_gig',
            'stripe_payment_id': f'pi_test_{uuid.uuid4().hex[:12]}',  # Always unique
            'status': 'completed'
        }
        defaults.update(overrides)
        return Payment.objects.create(**defaults)
    
    def test_payment_creation(self):
        """Test basic payment creation"""
        payment = self.create_unique_payment()
        self.assertEqual(payment.user, self.user)
        self.assertEqual(payment.gig, self.gig)
        self.assertEqual(payment.amount, Decimal('9.99'))
        self.assertEqual(payment.payment_type, 'featured_gig')
        self.assertEqual(payment.status, 'completed')
    
    def test_payment_type_choices(self):
        """Test payment type validation"""
        # Test valid payment types
        valid_types = ['gig_posting', 'featured_gig', 'premium_profile', 'application_boost']
        
        for payment_type in valid_types:
            payment = self.create_unique_payment(payment_type=payment_type)
            self.assertEqual(payment.payment_type, payment_type)
        
        # Test invalid payment type should raise validation error
        with self.assertRaises(ValidationError):
            payment_data = {
                'user': self.user,
                'gig': self.gig,
                'amount': Decimal('9.99'),
                'payment_type': 'invalid_type',  # Invalid choice
                'stripe_payment_id': f'pi_test_{uuid.uuid4().hex[:12]}',
                'status': 'completed'
            }
            payment = Payment(**payment_data)
            payment.full_clean()  # This triggers validation
    
    def test_payment_string_representation(self):
        """Test payment __str__ method"""
        payment = self.create_unique_payment()
        # Fixed to match your actual __str__ format:
        expected_str = f'{self.user.username} - ${payment.amount} - Featured Gig Upgrade'
        self.assertEqual(str(payment), expected_str)
    
    def test_payment_amount_precision(self):
        """Test payment amount decimal precision"""
        payment = self.create_unique_payment(amount=Decimal('123.45'))
        self.assertEqual(payment.amount, Decimal('123.45'))
        
        # Test with more precision
        payment2 = self.create_unique_payment(amount=Decimal('99.999'))
        # Should keep the precision as defined in model
        self.assertEqual(payment2.amount, Decimal('99.999'))
    
    def test_payment_status_choices(self):
        """Test payment status validation"""
        # Test all valid statuses
        valid_statuses = ['pending', 'completed', 'failed', 'refunded']
        
        for status in valid_statuses:
            payment = self.create_unique_payment(status=status)
            self.assertEqual(payment.status, status)
    
    def test_payment_user_relationship(self):
        """Test payment-user relationship"""
        payment = self.create_unique_payment()
        self.assertEqual(payment.user, self.user)
        
        # Test the related_name 'payments'
        user_payments = self.user.payments.all()
        self.assertIn(payment, user_payments)
    
    def test_payment_gig_relationship(self):
        """Test payment-gig relationship"""
        payment = self.create_unique_payment()
        self.assertEqual(payment.gig, self.gig)
        
        # Test SET_NULL on gig deletion
        gig_id = self.gig.id
        self.gig.delete()
        payment.refresh_from_db()
        self.assertIsNone(payment.gig)  # Should be None due to SET_NULL
    
    def test_payment_without_gig(self):
        """Test payment creation without associated gig"""
        payment = self.create_unique_payment(gig=None)
        self.assertIsNone(payment.gig)
        self.assertEqual(payment.user, self.user)
    
    def test_stripe_payment_id_uniqueness(self):
        """Test Stripe payment ID uniqueness constraint"""
        # Create first payment
        stripe_id = f'pi_test_{uuid.uuid4().hex[:12]}'
        payment1 = self.create_unique_payment(stripe_payment_id=stripe_id)
        
        # Try to create second payment with same stripe_payment_id
        with self.assertRaises(Exception):  # Should be IntegrityError
            Payment.objects.create(
                user=self.user,
                gig=self.gig,
                amount=Decimal('19.99'),
                payment_type='premium_profile',
                stripe_payment_id=stripe_id,  # Duplicate!
                status='pending'
            )
    
    def test_payment_status_workflow(self):
        """Test payment status transitions"""
        # Create pending payment
        payment = self.create_unique_payment(status='pending')
        self.assertEqual(payment.status, 'pending')
        
        # Update to completed
        payment.status = 'completed'
        payment.save()
        self.assertEqual(payment.status, 'completed')
        
        # Test refund
        payment.status = 'refunded'
        payment.save()
        self.assertEqual(payment.status, 'refunded')


class PaymentHistoryModelTest(TestCase):
    def setUp(self):
        """Set up test data for payment history tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.gig = Gig.objects.create(
            title='Test Gig',
            description='Test description',
            employer=self.user,
            budget=Decimal('100.00'),
            category='web_development'
        )
        
        self.payment = Payment.objects.create(
            user=self.user,
            gig=self.gig,
            amount=Decimal('9.99'),
            payment_type='featured_gig',
            stripe_payment_id=f'pi_test_{uuid.uuid4().hex[:12]}',
            status='completed'
        )
    
    def test_payment_history_creation(self):
        """Test payment history record creation"""
        history = PaymentHistory.objects.create(
            payment=self.payment,
            old_status='pending',
            new_status='completed',
            changed_by=self.user
        )
        
        self.assertEqual(history.payment, self.payment)
        self.assertEqual(history.old_status, 'pending')
        self.assertEqual(history.new_status, 'completed')
        self.assertEqual(history.changed_by, self.user)
    
    def test_payment_history_string_representation(self):
        """Test payment history string representation"""
        history = PaymentHistory.objects.create(
            payment=self.payment,
            old_status='pending',
            new_status='completed',
            changed_by=self.user
        )
        
        # Fixed to match your actual __str__ format:
        expected_str = f'Payment {self.payment.id}: pending → completed'
        self.assertEqual(str(history), expected_str)
    
    def test_payment_history_relationship(self):
        """Test payment-history relationship"""
        history = PaymentHistory.objects.create(
            payment=self.payment,
            old_status='pending',
            new_status='completed',
            changed_by=self.user
        )
        
        # Test that history is linked to payment
        self.assertEqual(history.payment, self.payment)
        
        # Fixed: Use the correct related_name 'history'
        payment_histories = self.payment.history.all()
        self.assertIn(history, payment_histories)
    
    def test_payment_history_without_user(self):
        """Test payment history creation without changed_by user"""
        history = PaymentHistory.objects.create(
            payment=self.payment,
            old_status='pending',
            new_status='completed',
            changed_by=None  # System change, no user
        )
        
        self.assertIsNone(history.changed_by)
        self.assertEqual(history.payment, self.payment)


class PaymentBusinessLogicTest(TestCase):
    """Test payment business logic and workflows"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testemployer',
            email='test@example.com',
            password='testpass123'
        )
        
        self.gig = Gig.objects.create(
            title='Test Gig for Featuring',
            description='Test description',
            employer=self.user,
            budget=Decimal('500.00'),
            category='web_development',
            is_featured=False  # Start as not featured
        )
    
    def test_featured_gig_payment_flow(self):
        """Test complete featured gig payment flow"""
        # Create payment for featuring gig
        payment = Payment.objects.create(
            user=self.user,
            gig=self.gig,
            amount=Decimal('9.99'),
            payment_type='featured_gig',
            stripe_payment_id=f'pi_test_{uuid.uuid4().hex[:12]}',
            status='pending'
        )
        
        # Simulate payment completion
        payment.status = 'completed'
        payment.save()
        
        # In real app, this would trigger gig.is_featured = True
        # Test that payment was processed
        self.assertEqual(payment.status, 'completed')
        self.assertEqual(payment.payment_type, 'featured_gig')
    
    def test_payment_failure_handling(self):
        """Test payment failure scenarios"""
        payment = Payment.objects.create(
            user=self.user,
            gig=self.gig,
            amount=Decimal('9.99'),
            payment_type='featured_gig',
            stripe_payment_id=f'pi_test_{uuid.uuid4().hex[:12]}',
            status='pending'
        )
        
        # Simulate payment failure
        payment.status = 'failed'
        payment.save()
        
        self.assertEqual(payment.status, 'failed')
        # In real app, gig should remain unfeatured
        
    def test_payment_refund_scenario(self):
        """Test payment refund handling"""
        # Create completed payment
        payment = Payment.objects.create(
            user=self.user,
            gig=self.gig,
            amount=Decimal('9.99'),
            payment_type='featured_gig',
            stripe_payment_id=f'pi_test_{uuid.uuid4().hex[:12]}',
            status='completed'
        )
        
        # Process refund
        payment.status = 'refunded'
        payment.save()
        
        self.assertEqual(payment.status, 'refunded')
        # In real app, this might trigger gig.is_featured = False