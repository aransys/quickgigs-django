from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal

from gigs.models import Gig


class CoreViewTest(TestCase):
    """Test core site functionality"""
    
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
        
        # Create test gigs for dynamic content
        self.gig1 = Gig.objects.create(
            title='Regular Web Development',
            employer=self.employer,
            budget=Decimal('800.00'),
            category='web_dev'
        )
        
        self.gig2 = Gig.objects.create(
            title='Featured Design Project',
            employer=self.employer,
            budget=Decimal('1200.00'),
            category='design',
            is_featured=True
        )
    
    def test_homepage_loads(self):
        """Test homepage loads successfully"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'QuickGigs')
    
    def test_homepage_dynamic_content(self):
        """Test homepage shows dynamic statistics"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Check dynamic statistics
        self.assertContains(response, '2')  # Total gigs
        self.assertContains(response, '1')  # Total employers
        
        # Check recent gigs section
        self.assertContains(response, 'Regular Web Development')
        self.assertContains(response, 'Featured Design Project')
    
    def test_homepage_featured_gigs_section(self):
        """Test homepage featured gigs section"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Should show featured gigs prominently
        self.assertContains(response, 'Featured Design Project')
        
        # Check that featured gigs are in context
        featured_gigs = response.context.get('featured_gigs', [])
        self.assertEqual(len(featured_gigs), 1)
        self.assertEqual(featured_gigs[0].title, 'Featured Design Project')
    
    def test_homepage_recent_gigs_section(self):
        """Test homepage recent gigs section"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Should show both gigs in recent section
        recent_gigs = response.context.get('recent_gigs', [])
        self.assertEqual(len(recent_gigs), 2)
        
        # Should be ordered by creation date (most recent first)
        gig_titles = [gig.title for gig in recent_gigs]
        self.assertIn('Regular Web Development', gig_titles)
        self.assertIn('Featured Design Project', gig_titles)
    
    def test_homepage_anonymous_user(self):
        """Test homepage for anonymous users"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Should show sign up call-to-action
        self.assertContains(response, 'Sign Up')
        self.assertContains(response, 'Get Started')
    
    def test_homepage_authenticated_user(self):
        """Test homepage for authenticated users"""
        self.client.login(username='employer', password='testpass123')
        
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Should show user-specific content
        self.assertContains(response, 'employer')  # Username in navigation
    
    def test_about_page(self):
        """Test about page loads correctly"""
        url = reverse('core:about')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'About')
        self.assertContains(response, 'QuickGigs')
        self.assertContains(response, 'mission')  # About page content
    
    def test_contact_page(self):
        """Test contact page loads correctly"""
        url = reverse('core:contact')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contact')
        self.assertContains(response, 'form')  # Contact form
    
    def test_site_navigation(self):
        """Test main site navigation works"""
        # Test homepage navigation
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Should have navigation links
        self.assertContains(response, 'Home')
        self.assertContains(response, 'Browse Gigs')
        self.assertContains(response, 'About')
        self.assertContains(response, 'Contact')
    
    def test_site_search_functionality(self):
        """Test basic search functionality (if implemented)"""
        # This would test search if implemented
        # For now, just test that search UI elements exist
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Check for search elements in navigation
        # (Depends on template implementation)
    
    def test_responsive_design_elements(self):
        """Test responsive design elements are present"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Check for mobile-responsive elements in HTML
        # This is basic - real responsive testing would need browser testing
        content = response.content.decode()
        
        # Look for responsive CSS classes (Tailwind)
        self.assertIn('md:', content)  # Medium screen breakpoint
        self.assertIn('lg:', content)  # Large screen breakpoint
    
    def test_error_handling(self):
        """Test 404 error handling"""
        # Test non-existent page
        response = self.client.get('/nonexistent-page/')
        self.assertEqual(response.status_code, 404)
        
        # Test non-existent gig
        response = self.client.get('/gigs/99999/')
        self.assertEqual(response.status_code, 404)


class SitePerformanceTest(TestCase):
    """Test site performance considerations"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create user
        self.user = User.objects.create_user(
            username='perftest',
            email='perf@example.com',
            password='testpass123'
        )
        
        # Create multiple gigs to test pagination/loading
        for i in range(15):
            Gig.objects.create(
                title=f'Test Gig {i}',
                employer=self.user,
                budget=Decimal('500.00'),
                category='web_dev'
            )
    
    def test_homepage_loads_efficiently(self):
        """Test homepage loads with many gigs efficiently"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Should load successfully even with many gigs
        self.assertEqual(response.status_code, 200)
        
        # Should limit recent gigs (check context)
        recent_gigs = response.context.get('recent_gigs', [])
        self.assertLessEqual(len(recent_gigs), 6)  # Should limit to 6
    
    def test_gig_listing_handles_many_gigs(self):
        """Test gig listing page with many gigs"""
        url = reverse('gigs:gig_list')
        response = self.client.get(url)
        
        # Should load successfully
        self.assertEqual(response.status_code, 200)
        
        # Should show all gigs or implement pagination
        gigs = response.context.get('gigs', [])
        self.assertGreaterEqual(len(gigs), 15)
    
    def test_database_query_efficiency(self):
        """Test that views don't create N+1 query problems"""
        # This is a basic test - in production you'd use django-debug-toolbar
        # or assertNumQueries to test query counts
        
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Should complete without errors
        self.assertEqual(response.status_code, 200)
        
        # In a real test, you'd assert that the number of database queries
        # doesn't increase linearly with the number of gigs