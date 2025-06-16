from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import datetime

from .models import Payment, PaymentHistory
from gigs.models import Gig


class PaymentModelTest(TestCase):
    """Test Payment model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testemployer',
            email='test@example.com',
            password='testpass123'
        )
        
        self.gig = Gig.objects.create(
            title='Test Gig for Payment',
            description='Test gig description',
            employer=self.user,
            budget=Decimal('500.00'),
            category='web_dev'
        )
        
        self.payment_data = {
            'user': self.user,
            'gig': self.gig,
            'amount': Decimal('9.99'),
            'payment_type': 'featured_gig',
            'status': 'pending',
            'stripe_payment_id': 'pi_test_1234567890',
            'description': 'Feature gig: Test Gig for Payment'
        }
    
    def test_payment_creation(self):
        """Test basic payment creation"""
        payment = Payment.objects.create(**self.payment_data)
        
        self.assertEqual(payment.user, self.user)
        self.assertEqual(payment.gig, self.gig)
        self.assertEqual(payment.amount, Decimal('9.99'))
        self.assertEqual(payment.payment_type, 'featured_gig')
        self.assertEqual(payment.status, 'pending')
        self.assertIsNotNone(payment.created_at)
        self.assertIsNotNone(payment.updated_at)
    
    def test_payment_string_representation(self):
        """Test payment __str__ method"""
        payment = Payment.objects.create(**self.payment_data)
        expected_str = f"Payment {payment.id} - {self.user.username} - $9.99"
        self.assertEqual(str(payment), expected_str)
    
    def test_payment_type_choices(self):
        """Test payment type validation"""
        valid_types = ['gig_posting', 'featured_gig', 'premium_profile', 'application_boost']
        
        for payment_type in valid_types:
            payment_data = self.payment_data.copy()
            payment_data['payment_type'] = payment_type
            payment = Payment.objects.create(**payment_data)
            self.assertEqual(payment.payment_type, payment_type)
    
    def test_payment_status_choices(self):
        """Test payment status validation"""
        valid_statuses = ['pending', 'completed', 'failed', 'refunded']
        
        for status in valid_statuses:
            payment_data = self.payment_data.copy()
            payment_data['status'] = status
            payment_data['stripe_payment_id'] = f'pi_test_{status}'
            payment = Payment.objects.create(**payment_data)
            self.assertEqual(payment.status, status)
    
    def test_payment_status_workflow(self):
        """Test payment status transitions"""
        payment = Payment.objects.create(**self.payment_data)
        
        # Start as pending
        self.assertEqual(payment.status, 'pending')
        
        # Complete payment
        payment.status = 'completed'
        payment.save()
        self.assertEqual(payment.status, 'completed')
        
        # Check updated_at is updated
        original_updated = payment.updated_at
        payment.status = 'refunded'
        payment.save()
        self.assertGreater(payment.updated_at, original_updated)
    
    def test_payment_without_gig(self):
        """Test payment creation without associated gig"""
        payment_data = self.payment_data.copy()
        payment_data['gig'] = None
        payment_data['payment_type'] = 'premium_profile'
        payment_data['description'] = 'Premium profile upgrade'
        
        payment = Payment.objects.create(**payment_data)
        self.assertIsNone(payment.gig)
        self.assertEqual(payment.payment_type, 'premium_profile')
    
    def test_stripe_payment_id_uniqueness(self):
        """Test Stripe payment ID uniqueness constraint"""
        # Create first payment
        payment1 = Payment.objects.create(**self.payment_data)
        
        # Try to create second payment with same Stripe ID
        payment_data2 = self.payment_data.copy()
        payment_data2['description'] = 'Different description'
        
        with self.assertRaises(Exception):  # IntegrityError or ValidationError
            Payment.objects.create(**payment_data2)
    
    def test_payment_amount_precision(self):
        """Test payment amount decimal precision"""
        payment_data = self.payment_data.copy()
        payment_data['amount'] = Decimal('999.99')
        payment = Payment.objects.create(**payment_data)
        self.assertEqual(payment.amount, Decimal('999.99'))
        
        # Test large amount
        payment_data['amount'] = Decimal('9999.99')
        payment_data['stripe_payment_id'] = 'pi_test_large'
        large_payment = Payment.objects.create(**payment_data)
        self.assertEqual(large_payment.amount, Decimal('9999.99'))
    
    def test_payment_user_relationship(self):
        """Test payment-user relationship"""
        payment = Payment.objects.create(**self.payment_data)
        
        # Test reverse relationship
        user_payments = self.user.payments.all()
        self.assertIn(payment, user_payments)
        
        # Test payment count
        self.assertEqual(self.user.payments.count(), 1)
    
    def test_payment_gig_relationship(self):
        """Test payment-gig relationship"""
        payment = Payment.objects.create(**self.payment_data)
        
        # Test gig can have multiple payments
        payment_data2 = self.payment_data.copy()
        payment_data2['stripe_payment_id'] = 'pi_test_second'
        payment_data2['description'] = 'Second payment attempt'
        payment2 = Payment.objects.create(**payment_data2)
        
        # Both payments should be associated with same gig
        self.assertEqual(payment.gig, self.gig)
        self.assertEqual(payment2.gig, self.gig)


class PaymentHistoryModelTest(TestCase):
    """Test PaymentHistory model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        
        self.payment = Payment.objects.create(
            user=self.user,
            amount=Decimal('9.99'),
            payment_type='featured_gig',
            status='pending',
            stripe_payment_id='pi_test_history',
            description='Test payment for history'
        )
    
    def test_payment_history_creation(self):
        """Test payment history record creation"""
        history = PaymentHistory.objects.create(
            payment=self.payment,
            old_status='pending',
            new_status='completed',
            changed_by=self.admin_user,
            notes='Payment completed successfully'
        )
        
        self.assertEqual(history.payment, self.payment)
        self.assertEqual(history.old_status, 'pending')
        self.assertEqual(history.new_status, 'completed')
        self.assertEqual(history.changed_by, self.admin_user)
        self.assertIsNotNone(history.created_at)
    
    def test_payment_history_without_user(self):
        """Test payment history creation without changed_by user"""
        history = PaymentHistory.objects.create(
            payment=self.payment,
            old_status='pending',
            new_status='failed',
            notes='Automatic failure - card declined'
        )
        
        self.assertIsNone(history.changed_by)
        self.assertEqual(history.notes, 'Automatic failure - card declined')
    
    def test_payment_history_relationship(self):
        """Test payment-history relationship"""
        # Create multiple history records
        history1 = PaymentHistory.objects.create(
            payment=self.payment,
            old_status='pending',
            new_status='completed',
            changed_by=self.admin_user
        )
        
        history2 = PaymentHistory.objects.create(
            payment=self.payment,
            old_status='completed',
            new_status='refunded',
            changed_by=self.admin_user,
            notes='Customer requested refund'
        )
        
        # Test reverse relationship
        payment_history = self.payment.history.all()
        self.assertEqual(payment_history.count(), 2)
        self.assertIn(history1, payment_history)
        self.assertIn(history2, payment_history)
    
    def test_payment_history_string_representation(self):
        """Test payment history string representation"""
        history = PaymentHistory.objects.create(
            payment=self.payment,
            old_status='pending',
            new_status='completed'
        )
        
        expected_str = f"Payment {self.payment.id}: pending → completed"
        self.assertEqual(str(history), expected_str)


class PaymentBusinessLogicTest(TestCase):
    """Test payment-related business logic"""
    
    def setUp(self):
        """Set up test data"""
        self.employer = User.objects.create_user(
            username='employer',
            email='employer@example.com',
            password='testpass123'
        )
        
        # Set user as employer
        self.employer.userprofile.user_type = 'employer'
        self.employer.userprofile.save()
        
        self.gig = Gig.objects.create(
            title='Test Gig',
            description='Test description',
            employer=self.employer,
            budget=Decimal('500.00'),
            category='web_dev',
            is_featured=False
        )
    
    def test_featured_gig_payment_flow(self):
        """Test complete featured gig payment flow"""
        # Initial state
        self.assertFalse(self.gig.is_featured)
        
        # Create pending payment
        payment = Payment.objects.create(
            user=self.employer,
            gig=self.gig,
            amount=Decimal('9.99'),
            payment_type='featured_gig',
            status='pending',
            stripe_payment_id='pi_test_featured',
            description=f'Feature gig: {self.gig.title}'
        )
        
        # Simulate successful payment
        payment.status = 'completed'
        payment.save()
        
        # Gig should now be marked as featured (in real app)
        # This would be done in the view, not automatically
        self.gig.is_featured = True
        self.gig.save()
        
        # Verify final state
        self.assertTrue(self.gig.is_featured)
        self.assertEqual(payment.status, 'completed')
    
    def test_payment_failure_handling(self):
        """Test payment failure scenarios"""
        payment = Payment.objects.create(
            user=self.employer,
            gig=self.gig,
            amount=Decimal('9.99'),
            payment_type='featured_gig',
            status='pending',
            stripe_payment_id='pi_test_fail'
        )
        
        # Simulate payment failure
        payment.status = 'failed'
        payment.save()
        
        # Gig should remain non-featured
        self.assertFalse(self.gig.is_featured)
        self.assertEqual(payment.status, 'failed')
    
    def test_payment_refund_scenario(self):
        """Test payment refund handling"""
        # Create completed payment
        payment = Payment.objects.create(
            user=self.employer,
            gig=self.gig,
            amount=Decimal('9.99'),
            payment_type='featured_gig',
            status='completed',
            stripe_payment_id='pi_test_refund'
        )
        
        # Gig was featured
        self.gig.is_featured = True
        self.gig.save()
        
        # Process refund
        payment.status = 'refunded'
        payment.save()
        
        # In real app, gig would be unfeatured
        self.gig.is_featured = False
        self.gig.save()
        
        self.assertEqual(payment.status, 'refunded')
        self.assertFalse(self.gig.is_featured)