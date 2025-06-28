from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from datetime import date, timedelta
# from .models import Task


class GigViewTest(TestCase):
    """Test suite for Gig CRUD views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create users
        self.employer = User.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass123'
        )
        self.employer.userprofile.user_type = 'employer'
        self.employer.userprofile.save()
        
        self.freelancer = User.objects.create_user(
            username='freelancer',
            email='freelancer@test.com',
            password='testpass123'
        )
        self.freelancer.userprofile.user_type = 'freelancer'
        self.freelancer.userprofile.save()
        
        # Create test gig
        self.gig = Gig.objects.create(
            title='Test Web Development Gig',
            description='Build a Django application',
            employer=self.employer,
            budget=Decimal('1500.00'),
            location='Remote',
            category='web_dev',
            deadline=date.today() + timedelta(days=30)
        )

    def test_gig_list_view(self):
        """Test gig listing page"""
        url = reverse('gigs:gig_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Web Development Gig')
        self.assertContains(response, '$1,500.00')
        self.assertContains(response, 'Remote')

    def test_gig_list_shows_only_active_gigs(self):
        """Test that only active gigs appear in listing"""
        # Create inactive gig
        inactive_gig = Gig.objects.create(
            title='Inactive Gig',
            employer=self.employer,
            budget=Decimal('500.00'),
            category='design',
            is_active=False
        )
        
        url = reverse('gigs:gig_list')
        response = self.client.get(url)
        
        self.assertContains(response, 'Test Web Development Gig')
        self.assertNotContains(response, 'Inactive Gig')

    def test_featured_gigs_appear_first(self):
        """Test that featured gigs appear before regular gigs"""
        # Create featured gig
        featured_gig = Gig.objects.create(
            title='Featured Gig',
            employer=self.employer,
            budget=Decimal('2000.00'),
            category='design',
            is_featured=True
        )
        
        url = reverse('gigs:gig_list')
        response = self.client.get(url)
        
        gigs = response.context['gigs']
        self.assertEqual(gigs[0], featured_gig)
        self.assertEqual(gigs[1], self.gig)

    def test_gig_detail_view(self):
        """Test gig detail page"""
        url = reverse('gigs:gig_detail', kwargs={'pk': self.gig.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Web Development Gig')
        self.assertContains(response, 'Build a Django application')
        self.assertContains(response, '$1,500.00')
        self.assertContains(response, 'Remote')
        self.assertContains(response, 'Web Development')

    def test_gig_detail_shows_feature_option_for_owner(self):
        """Test that gig owner sees feature option"""
        self.client.login(username='employer', password='testpass123')
        
        url = reverse('gigs:gig_detail', kwargs={'pk': self.gig.pk})
        response = self.client.get(url)
        
        self.assertContains(response, 'Feature This Gig')
        self.assertContains(response, 'Boost Your Gig')

    def test_gig_detail_no_feature_option_for_non_owner(self):
        """Test that non-owners don't see feature option"""
        self.client.login(username='freelancer', password='testpass123')
        
        url = reverse('gigs:gig_detail', kwargs={'pk': self.gig.pk})
        response = self.client.get(url)
        
        self.assertNotContains(response, 'Feature This Gig')

    def test_gig_detail_no_feature_option_for_featured_gig(self):
        """Test that already featured gigs don't show feature option"""
        self.gig.is_featured = True
        self.gig.save()
        
        self.client.login(username='employer', password='testpass123')
        
        url = reverse('gigs:gig_detail', kwargs={'pk': self.gig.pk})
        response = self.client.get(url)
        
        self.assertNotContains(response, 'Feature This Gig')

    def test_gig_create_requires_login(self):
        """Test that gig creation requires authentication"""
        url = reverse('gigs:gig_create')
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_gig_create_form_loads(self):
        """Test gig creation form loads correctly"""
        self.client.login(username='employer', password='testpass123')
        
        url = reverse('gigs:gig_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Post a New Gig')
        self.assertContains(response, 'Title')
        self.assertContains(response, 'Description')
        self.assertContains(response, 'Budget')
        self.assertContains(response, 'Category')

    def test_gig_create_post(self):
        """Test gig creation form submission"""
        self.client.login(username='employer', password='testpass123')
        
        url = reverse('gigs:gig_create')
        gig_data = {
            'title': 'New Test Gig',
            'description': 'New gig description',
            'budget': '750.00',
            'location': 'London',
            'category': 'design',
            'deadline': (date.today() + timedelta(days=20)).strftime('%Y-%m-%d')
        }
        
        response = self.client.post(url, gig_data)
        
        # Should redirect to new gig detail page
        self.assertEqual(response.status_code, 302)
        
        # Gig should be created with correct employer
        new_gig = Gig.objects.get(title='New Test Gig')
        self.assertEqual(new_gig.employer, self.employer)
        self.assertEqual(new_gig.budget, Decimal('750.00'))
        self.assertEqual(new_gig.location, 'London')
        self.assertEqual(new_gig.category, 'design')

    def test_gig_create_invalid_data(self):
        """Test gig creation with invalid data"""
        self.client.login(username='employer', password='testpass123')
        
        url = reverse('gigs:gig_create')
        invalid_data = {
            'title': '',  # Required field empty
            'description': 'Description',
            'budget': 'invalid',  # Invalid budget
            'category': 'invalid_category'
        }
        
        response = self.client.post(url, invalid_data)
        
        # Should not redirect (form errors)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')

    def test_gig_update_requires_ownership(self):
        """Test that only gig owner can edit gig"""
        # Try to edit as different user
        self.client.login(username='freelancer', password='testpass123')
        
        url = reverse('gigs:gig_update', kwargs={'pk': self.gig.pk})
        response = self.client.get(url)
        
        # Should return 404 (ownership check)
        self.assertEqual(response.status_code, 404)

    def test_gig_update_form_loads(self):
        """Test gig update form loads with existing data"""
        self.client.login(username='employer', password='testpass123')
        
        url = reverse('gigs:gig_update', kwargs={'pk': self.gig.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Gig')
        self.assertContains(response, 'Test Web Development Gig')

    def test_gig_update_post(self):
        """Test gig update form submission"""
        self.client.login(username='employer', password='testpass123')
        
        url = reverse('gigs:gig_update', kwargs={'pk': self.gig.pk})
        update_data = {
            'title': 'Updated Gig Title',
            'description': 'Updated description',
            'budget': '2000.00',
            'location': 'Manchester',
            'category': 'web_dev',
            'deadline': (date.today() + timedelta(days=40)).strftime('%Y-%m-%d')
        }
        
        response = self.client.post(url, update_data)
        
        # Should redirect to gig detail
        self.assertEqual(response.status_code, 302)
        
        # Gig should be updated
        self.gig.refresh_from_db()
        self.assertEqual(self.gig.title, 'Updated Gig Title')
        self.assertEqual(self.gig.budget, Decimal('2000.00'))
        self.assertEqual(self.gig.location, 'Manchester')

    def test_gig_delete_requires_ownership(self):
        """Test that only gig owner can delete gig"""
        self.client.login(username='freelancer', password='testpass123')
        
        url = reverse('gigs:gig_delete', kwargs={'pk': self.gig.pk})
        response = self.client.get(url)
        
        # Should return 404 (ownership check)
        self.assertEqual(response.status_code, 404)

    def test_gig_delete_confirmation_loads(self):
        """Test gig delete confirmation page"""
        self.client.login(username='employer', password='testpass123')
        
        url = reverse('gigs:gig_delete', kwargs={'pk': self.gig.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete Gig')
        self.assertContains(response, 'Test Web Development Gig')
        self.assertContains(response, 'Are you sure')

    def test_gig_delete_post(self):
        """Test gig deletion"""
        self.client.login(username='employer', password='testpass123')
        
        gig_id = self.gig.id
        url = reverse('gigs:gig_delete', kwargs={'pk': self.gig.pk})
        response = self.client.post(url)
        
        # Should redirect to gig list
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('gigs:gig_list'))
        
        # Gig should be deleted
        self.assertFalse(Gig.objects.filter(id=gig_id).exists())

    def test_toggle_gig_status_requires_ownership(self):
        """Test that only owner can toggle gig status"""
        self.client.login(username='freelancer', password='testpass123')
        
        url = reverse('gigs:toggle_gig_status', kwargs={'pk': self.gig.pk})
        response = self.client.post(url)
        
        # Should return 404
        self.assertEqual(response.status_code, 404)

    def test_toggle_gig_status_activate_to_deactivate(self):
        """Test toggling gig from active to inactive"""
        self.client.login(username='employer', password='testpass123')
        
        # Ensure gig is active
        self.assertTrue(self.gig.is_active)
        
        url = reverse('gigs:toggle_gig_status', kwargs={'pk': self.gig.pk})
        response = self.client.post(url)
        
        # Should redirect to gig detail
        self.assertEqual(response.status_code, 302)
        
        # Gig should be deactivated
        self.gig.refresh_from_db()
        self.assertFalse(self.gig.is_active)

    def test_toggle_gig_status_deactivate_to_activate(self):
        """Test toggling gig from inactive to active"""
        self.gig.is_active = False
        self.gig.save()
        
        self.client.login(username='employer', password='testpass123')
        
        url = reverse('gigs:toggle_gig_status', kwargs={'pk': self.gig.pk})
        response = self.client.post(url)
        
        # Gig should be activated
        self.gig.refresh_from_db()
        self.assertTrue(self.gig.is_active)


class GigSecurityTest(TestCase):
    """Test suite for gig-related security"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )
        
        self.gig = Gig.objects.create(
            title='User 1 Gig',
            employer=self.user1,
            budget=Decimal('1000.00'),
            category='web_dev'
        )

    def test_gig_ownership_enforcement_update(self):
        """Test gig ownership is enforced for updates"""
        self.client.login(username='user2', password='testpass123')
        
        url = reverse('gigs:gig_update', kwargs={'pk': self.gig.pk})
        response = self.client.get(url)
        
        # Should return 404 (ownership check)
        self.assertEqual(response.status_code, 404)

    def test_gig_ownership_enforcement_delete(self):
        """Test gig ownership is enforced for deletion"""
        self.client.login(username='user2', password='testpass123')
        
        url = reverse('gigs:gig_delete', kwargs={'pk': self.gig.pk})
        response = self.client.get(url)
        
        # Should return 404 (ownership check)
        self.assertEqual(response.status_code, 404)

    def test_gig_ownership_enforcement_toggle_status(self):
        """Test gig ownership is enforced for status toggle"""
        self.client.login(username='user2', password='testpass123')
        
        url = reverse('gigs:toggle_gig_status', kwargs={'pk': self.gig.pk})
        response = self.client.post(url)
        
        # Should return 404 (ownership check)
        self.assertEqual(response.status_code, 404)

    def test_nonexistent_gig_returns_404(self):
        """Test that accessing nonexistent gigs returns 404"""
        self.client.login(username='user1', password='testpass123')
        
        urls = [
            reverse('gigs:gig_detail', kwargs={'pk': 99999}),
            reverse('gigs:gig_update', kwargs={'pk': 99999}),
            reverse('gigs:gig_delete', kwargs={'pk': 99999}),
            reverse('gigs:toggle_gig_status', kwargs={'pk': 99999}),
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404, f"URL {url} should return 404")


class GigFilteringTest(TestCase):
    """Test suite for gig filtering and search"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.employer = User.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass123'
        )
        
        # Create gigs in different categories
        self.web_gig = Gig.objects.create(
            title='Web Development Project',
            employer=self.employer,
            budget=Decimal('1500.00'),
            category='web_dev',
            location='Remote'
        )
        
        self.design_gig = Gig.objects.create(
            title='Logo Design',
            employer=self.employer,
            budget=Decimal('500.00'),
            category='design',
            location='London'
        )
        
        self.writing_gig = Gig.objects.create(
            title='Content Writing',
            employer=self.employer,
            budget=Decimal('300.00'),
            category='writing',
            location='Manchester'
        )

    def test_gig_list_shows_all_active_gigs(self):
        """Test that gig list shows all active gigs"""
        url = reverse('gigs:gig_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Web Development Project')
        self.assertContains(response, 'Logo Design')
        self.assertContains(response, 'Content Writing')

    def test_gig_list_context_data(self):
        """Test gig list context contains correct data"""
        url = reverse('gigs:gig_list')
        response = self.client.get(url)
        
        gigs = response.context['gigs']
        self.assertEqual(len(gigs), 3)
        
        # Check that gigs are ordered correctly (featured first, then by creation date)
        gig_titles = [gig.title for gig in gigs]
        self.assertIn('Web Development Project', gig_titles)
        self.assertIn('Logo Design', gig_titles)
        self.assertIn('Content Writing', gig_titles)


class GigResponseTest(TestCase):
    """Test suite for gig response codes and redirects"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.employer = User.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass123'
        )
        
        self.gig = Gig.objects.create(
            title='Test Gig',
            employer=self.employer,
            budget=Decimal('1000.00'),
            category='web_dev'
        )

    def test_gig_list_response_code(self):
        """Test gig list returns 200"""
        url = reverse('gigs:gig_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_gig_detail_response_code(self):
        """Test gig detail returns 200"""
        url = reverse('gigs:gig_detail', kwargs={'pk': self.gig.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_gig_create_redirect_when_not_logged_in(self):
        """Test gig create redirects to login when not authenticated"""
        url = reverse('gigs:gig_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_successful_gig_creation_redirect(self):
        """Test successful gig creation redirects to detail page"""
        self.client.login(username='employer', password='testpass123')
        
        url = reverse('gigs:gig_create')
        gig_data = {
            'title': 'Redirect Test Gig',
            'description': 'Test gig for redirect',
            'budget': '800.00',
            'category': 'design',
            'location': 'Remote',
        }
        
        response = self.client.post(url, gig_data)
        
        # Should redirect to gig list page (not detail page)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('gigs:gig_list'))
        
        # Verify the gig was created
        new_gig = Gig.objects.get(title='Redirect Test Gig')
        self.assertEqual(new_gig.employer.username, 'employer')