from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages import get_messages
from decimal import Decimal
from unittest.mock import patch, MagicMock

from gigs.models import Gig
from .models import Payment


class PaymentViewTest(TestCase):
    """Test payment view functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create employer user
        self.employer = User.objects.create_user(
            username='employer',
            email='employer@example.com',
            password='testpass123'
        )
        self.employer.userprofile.user_type = 'employer'
        self.employer.userprofile.save()
        
        # Create freelancer user
        self.freelancer = User.objects.create_user(
            username='freelancer',
            email='freelancer@example.com',
            password='testpass123'
        )
        
        # Create test gig
        self.gig = Gig.objects.create(
            title='Test Payment Gig',
            description='Test gig for payment testing',
            employer=self.employer,
            budget=Decimal('500.00'),
            category='web_dev',
            is_featured=False
        )
    
    def test_feature_gig_checkout_requires_login(self):
        """Test that feature gig checkout requires authentication"""
        url = reverse('payments:feature_gig_checkout', kwargs={'gig_id': self.gig.id})
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_feature_gig_checkout_requires_ownership(self):
        """Test that only gig owner can feature their gig"""
        # Login as freelancer (not owner)
        self.client.login(username='freelancer', password='testpass123')
        
        url = reverse('payments:feature_gig_checkout', kwargs={'gig_id': self.gig.id})
        response = self.client.get(url)
        
        # Should return 404 (get_object_or_404 with employer=request.user)
        self.assertEqual(response.status_code, 404)
    
    def test_feature_already_featured_gig(self):
        """Test attempting to feature already featured gig"""
        # Login as employer
        self.client.login(username='employer', password='testpass123')
        
        # Mark gig as featured
        self.gig.is_featured = True
        self.gig.save()
        
        url = reverse('payments:feature_gig_checkout', kwargs={'gig_id': self.gig.id})
        response = self.client.get(url)
        
        # Should redirect with warning message
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('already featured' in str(m) for m in messages))
    
    @patch('payments.views.stripe.checkout.Session.create')
    def test_successful_checkout_session_creation(self, mock_stripe_create):
        """Test successful Stripe checkout session creation"""
        # Mock Stripe response
        mock_session = MagicMock()
        mock_session.id = 'cs_test_123'
        mock_session.url = 'https://checkout.stripe.com/c/pay/cs_test_123'
        mock_stripe_create.return_value = mock_session
        
        # Login as employer
        self.client.login(username='employer', password='testpass123')
        
        url = reverse('payments:feature_gig_checkout', kwargs={'gig_id': self.gig.id})
        response = self.client.get(url)
        
        # Should redirect to Stripe checkout
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, mock_session.url)
        
        # Payment record should be created
        payment = Payment.objects.get(gig=self.gig, payment_type='featured_gig')
        self.assertEqual(payment.user, self.employer)
        self.assertEqual(payment.amount, Decimal('9.99'))
        self.assertEqual(payment.status, 'pending')
        self.assertEqual(payment.stripe_payment_id, 'cs_test_123')
    
    @patch('payments.views.stripe.checkout.Session.create')
    def test_stripe_api_error_handling(self, mock_stripe_create):
        """Test handling of Stripe API errors"""
        # Mock Stripe API error
        mock_stripe_create.side_effect = Exception('Stripe API Error')
        
        # Login as employer
        self.client.login(username='employer', password='testpass123')
        
        url = reverse('payments:feature_gig_checkout', kwargs={'gig_id': self.gig.id})
        response = self.client.get(url)
        
        # Should redirect back to gig detail with error message
        self.assertEqual(response.status_code, 302)
        self.assertIn(f'/gigs/{self.gig.id}/', response.url)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Error creating payment session' in str(m) for m in messages))
    
    def test_payment_success_view(self):
        """Test payment success handling"""
        # Create pending payment
        payment = Payment.objects.create(
            user=self.employer,
            gig=self.gig,
            amount=Decimal('9.99'),
            payment_type='featured_gig',
            status='pending',
            stripe_payment_id='cs_test_success'
        )
        
        url = reverse('payments:payment_success', kwargs={'gig_id': self.gig.id})
        response = self.client.get(url)
        
        # Should render success page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Payment Successful')
        self.assertContains(response, self.gig.title)
        
        # Gig should be featured
        self.gig.refresh_from_db()
        self.assertTrue(self.gig.is_featured)
        
        # Payment should be completed
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'completed')
    
    def test_payment_cancel_view(self):
        """Test payment cancellation handling"""
        # Create pending payment
        payment = Payment.objects.create(
            user=self.employer,
            gig=self.gig,
            amount=Decimal('9.99'),
            payment_type='featured_gig',
            status='pending',
            stripe_payment_id='cs_test_cancel'
        )
        
        url = reverse('payments:payment_cancel', kwargs={'gig_id': self.gig.id})
        response = self.client.get(url)
        
        # Should render cancel page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Payment Cancelled')
        self.assertContains(response, self.gig.title)
        
        # Gig should remain not featured
        self.gig.refresh_from_db()
        self.assertFalse(self.gig.is_featured)
        
        # Payment should be failed
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'failed')
    
    def test_payment_history_view_requires_login(self):
        """Test payment history requires authentication"""
        url = reverse('payments:payment_history')
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_payment_history_view_with_payments(self):
        """Test payment history display with existing payments"""
        # Create test payments
        payment1 = Payment.objects.create(
            user=self.employer,
            gig=self.gig,
            amount=Decimal('9.99'),
            payment_type='featured_gig',
            status='completed',
            description='Featured gig payment'
        )
        
        payment2 = Payment.objects.create(
            user=self.employer,
            amount=Decimal('19.99'),
            payment_type='premium_profile',
            status='completed',
            description='Premium profile upgrade'
        )
        
        # Login and view history
        self.client.login(username='employer', password='testpass123')
        url = reverse('payments:payment_history')
        response = self.client.get(url)
        
        # Should display both payments
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Payment History')
        self.assertContains(response, payment1.description)
        self.assertContains(response, payment2.description)
        self.assertContains(response, '£9.99')
        self.assertContains(response, '£19.99')
    
    def test_payment_history_view_empty_state(self):
        """Test payment history with no payments"""
        # Login as user with no payments
        self.client.login(username='freelancer', password='testpass123')
        url = reverse('payments:payment_history')
        response = self.client.get(url)
        
        # Should show empty state
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No Payments Yet')
    
    def test_payment_history_user_isolation(self):
        """Test users only see their own payment history"""
        # Create payment for employer
        employer_payment = Payment.objects.create(
            user=self.employer,
            amount=Decimal('9.99'),
            payment_type='featured_gig',
            status='completed'
        )
        
        # Create different user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        other_payment = Payment.objects.create(
            user=other_user,
            amount=Decimal('19.99'),
            payment_type='premium_profile',
            status='completed'
        )
        
        # Login as employer
        self.client.login(username='employer', password='testpass123')
        url = reverse('payments:payment_history')
        response = self.client.get(url)
        
        # Should only see own payment
        self.assertContains(response, '£9.99')
        self.assertNotContains(response, '£19.99')


class PaymentIntegrationTest(TestCase):
    """Test payment system integration with other components"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.employer = User.objects.create_user(
            username='employer',
            email='employer@example.com',
            password='testpass123'
        )
        self.employer.userprofile.user_type = 'employer'
        self.employer.userprofile.save()
        
        self.gig = Gig.objects.create(
            title='Integration Test Gig',
            description='Test gig for integration testing',
            employer=self.employer,
            budget=Decimal('750.00'),
            category='design'
        )
    
    def test_gig_detail_page_shows_feature_button(self):
        """Test that gig detail page shows feature button for owners"""
        self.client.login(username='employer', password='testpass123')
        
        url = reverse('gigs:gig_detail', kwargs={'pk': self.gig.id})
        response = self.client.get(url)
        
        # Should show feature button for non-featured gig
        self.assertContains(response, 'Feature This Gig')
        self.assertContains(response, '£9.99')
    
    def test_gig_detail_page_hides_feature_button_for_featured(self):
        """Test that featured gigs don't show feature button"""
        self.gig.is_featured = True
        self.gig.save()
        
        self.client.login(username='employer', password='testpass123')
        
        url = reverse('gigs:gig_detail', kwargs={'pk': self.gig.id})
        response = self.client.get(url)
        
        # Should show featured status, not feature button
        self.assertContains(response, 'Featured Gig')
        self.assertNotContains(response, 'Feature This Gig')
    
    def test_featured_gigs_appear_first_in_listing(self):
        """Test that featured gigs appear at top of listings"""
        # Create regular gig
        regular_gig = Gig.objects.create(
            title='Regular Gig',
            employer=self.employer,
            budget=Decimal('300.00'),
            category='writing'
        )
        
        # Feature our test gig
        self.gig.is_featured = True
        self.gig.save()
        
        url = reverse('gigs:gig_list')
        response = self.client.get(url)
        
        # Featured gig should appear before regular gig
        gig_titles = [gig.title for gig in response.context['gigs']]
        featured_index = gig_titles.index(self.gig.title)
        regular_index = gig_titles.index(regular_gig.title)
        
        self.assertLess(featured_index, regular_index)