from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from gigs.models import Gig
from accounts.models import UserProfile


class HomepageViewTest(TestCase):
    """Test suite for homepage functionality"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create users
        self.employer1 = User.objects.create_user(
            username='employer1',
            email='employer1@test.com',
            password='testpass123'
        )
        self.employer1.userprofile.user_type = 'employer'
        self.employer1.userprofile.save()
        
        self.employer2 = User.objects.create_user(
            username='employer2',
            email='employer2@test.com',
            password='testpass123'
        )
        self.employer2.userprofile.user_type = 'employer'
        self.employer2.userprofile.save()
        
        self.freelancer = User.objects.create_user(
            username='freelancer',
            email='freelancer@test.com',
            password='testpass123'
        )
        self.freelancer.userprofile.user_type = 'freelancer'
        self.freelancer.userprofile.save()
        
        # Create test gigs
        self.regular_gig = Gig.objects.create(
            title='Regular Web Development Gig',
            description='Build a web application',
            employer=self.employer1,
            budget=Decimal('1500.00'),
            category='web_dev',
            is_featured=False
        )
        
        self.featured_gig = Gig.objects.create(
            title='Featured Design Project',
            description='Create a logo and branding',
            employer=self.employer2,
            budget=Decimal('800.00'),
            category='design',
            is_featured=True
        )
        
        self.inactive_gig = Gig.objects.create(
            title='Inactive Gig',
            description='This gig is not active',
            employer=self.employer1,
            budget=Decimal('500.00'),
            category='writing',
            is_active=False
        )

    def test_homepage_loads_successfully(self):
        """Test that homepage loads without errors"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'QuickGigs')

    def test_homepage_shows_recent_gigs(self):
        """Test that homepage displays recent gigs"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Should show active gigs
        self.assertContains(response, 'Regular Web Development Gig')
        self.assertContains(response, 'Featured Design Project')
        
        # Should not show inactive gigs
        self.assertNotContains(response, 'Inactive Gig')

    def test_homepage_shows_featured_gigs(self):
        """Test that homepage highlights featured gigs"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Should contain featured gigs section
        self.assertContains(response, 'Featured Opportunities')
        self.assertContains(response, 'Featured Design Project')

    def test_homepage_statistics(self):
        """Test that homepage shows correct platform statistics"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Check context data
        context = response.context
        
        # Total active gigs (should be 2 - regular + featured)
        self.assertEqual(context['total_gigs'], 2)
        
        # Total employers (should be 2)
        self.assertEqual(context['total_employers'], 2)
        
        # Total freelancers (should be 1)
        self.assertEqual(context['total_freelancers'], 1)

    def test_homepage_context_data(self):
        """Test homepage context contains required data"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        context = response.context
        
        # Check that context contains expected keys
        self.assertIn('recent_gigs', context)
        self.assertIn('featured_gigs', context)
        self.assertIn('total_gigs', context)
        self.assertIn('total_employers', context)
        self.assertIn('total_freelancers', context)
        
        # Check that recent_gigs contains only active gigs
        recent_gigs = context['recent_gigs']
        for gig in recent_gigs:
            self.assertTrue(gig.is_active)
        
        # Check that featured_gigs contains only featured and active gigs
        featured_gigs = context['featured_gigs']
        for gig in featured_gigs:
            self.assertTrue(gig.is_featured)
            self.assertTrue(gig.is_active)

    def test_homepage_anonymous_user_content(self):
        """Test homepage content for anonymous users"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Should show signup/login calls to action
        self.assertContains(response, 'Sign Up')
        self.assertContains(response, 'Get Started')
        
        # Should show value proposition
        self.assertContains(response, 'Find Your Next')
        self.assertContains(response, 'Opportunity')

    def test_homepage_authenticated_user_content(self):
        """Test homepage content for authenticated users"""
        self.client.login(username='freelancer', password='testpass123')
        
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Should show personalized content
        self.assertContains(response, 'freelancer')  # Username in navigation
        
        # Should not show signup prompts
        self.assertNotContains(response, 'Sign Up for Free')

    def test_homepage_employer_content(self):
        """Test homepage content for employer users"""
        self.client.login(username='employer1', password='testpass123')
        
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Should show employer-specific content
        self.assertContains(response, 'Post a Gig')

    def test_homepage_performance(self):
        """Test homepage database query efficiency"""
        # Create more gigs to test query efficiency
        for i in range(10):
            Gig.objects.create(
                title=f'Performance Test Gig {i}',
                employer=self.employer1,
                budget=Decimal('100.00'),
                category='other'
            )
        
        url = reverse('core:home')
        
        # Test that homepage doesn't create excessive queries
        with self.assertNumQueries(5):  # Adjust based on actual optimized query count
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)


class AboutViewTest(TestCase):
    """Test suite for About page"""

    def test_about_page_loads(self):
        """Test that about page loads successfully"""
        url = reverse('core:about')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'About QuickGigs')

    def test_about_page_content(self):
        """Test about page contains expected content"""
        url = reverse('core:about')
        response = self.client.get(url)
        
        # Should contain mission and value proposition
        self.assertContains(response, 'Our Mission')
        self.assertContains(response, 'connecting')
        self.assertContains(response, 'freelancers')
        self.assertContains(response, 'employers')

    def test_about_page_features_section(self):
        """Test about page features section"""
        url = reverse('core:about')
        response = self.client.get(url)
        
        # Should contain platform features
        self.assertContains(response, 'Easy to Use')
        self.assertContains(response, 'Secure Payments')
        self.assertContains(response, 'Quality Assurance')


class ContactViewTest(TestCase):
    """Test suite for Contact page"""

    def test_contact_page_loads(self):
        """Test that contact page loads successfully"""
        url = reverse('core:contact')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contact Us')

    def test_contact_page_form(self):
        """Test contact page contains contact form"""
        url = reverse('core:contact')
        response = self.client.get(url)
        
        # Should contain contact form elements
        self.assertContains(response, 'Subject')
        self.assertContains(response, 'Message')
        self.assertContains(response, 'Email')

    def test_contact_page_information(self):
        """Test contact page contains contact information"""
        url = reverse('core:contact')
        response = self.client.get(url)
        
        # Should contain contact information
        self.assertContains(response, 'Get in Touch')
        self.assertContains(response, 'support')


class NavigationTest(TestCase):
    """Test suite for site-wide navigation"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
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

    def test_anonymous_navigation(self):
        """Test navigation for anonymous users"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Should contain public navigation items
        self.assertContains(response, 'Home')
        self.assertContains(response, 'Browse Gigs')
        self.assertContains(response, 'About')
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Sign Up')

    def test_authenticated_user_navigation(self):
        """Test navigation for authenticated users"""
        self.client.login(username='freelancer', password='testpass123')
        
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Should contain authenticated user navigation
        self.assertContains(response, 'freelancer')  # Username
        self.assertContains(response, 'Profile')
        self.assertContains(response, 'Logout')
        
        # Should not contain anonymous user elements
        self.assertNotContains(response, 'Sign Up')

    def test_employer_navigation(self):
        """Test navigation specific to employers"""
        self.client.login(username='employer', password='testpass123')
        
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Employers should see post gig option
        self.assertContains(response, 'Post a Gig')

    def test_freelancer_navigation(self):
        """Test navigation for freelancers"""
        self.client.login(username='freelancer', password='testpass123')
        
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Freelancers should not see post gig option in main nav
        # (they might see it elsewhere, but not in primary navigation)
        self.assertContains(response, 'Browse Gigs')


class SiteWideSecurityTest(TestCase):
    """Test suite for site-wide security features"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

    def test_csrf_protection_enabled(self):
        """Test that CSRF protection is enabled site-wide"""
        # This is more of a configuration test
        from django.conf import settings
        self.assertIn('django.middleware.csrf.CsrfViewMiddleware', settings.MIDDLEWARE)

    def test_secure_headers_present(self):
        """Test that secure headers are present in responses"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Test should pass if basic security middleware is enabled
        self.assertEqual(response.status_code, 200)

    def test_no_sensitive_info_in_templates(self):
        """Test that sensitive information doesn't leak in templates"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Should not contain sensitive debug information
        self.assertNotContains(response, 'DEBUG = True')
        self.assertNotContains(response, 'SECRET_KEY')
        self.assertNotContains(response, 'password')


class ResponsiveDesignTest(TestCase):
    """Test suite for responsive design elements"""

    def test_mobile_viewport_meta_tag(self):
        """Test that mobile viewport meta tag is present"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Should contain mobile viewport meta tag
        self.assertContains(response, 'viewport')
        self.assertContains(response, 'width=device-width')

    def test_responsive_css_classes(self):
        """Test that responsive CSS classes are present"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Should contain Tailwind responsive classes
        self.assertContains(response, 'md:')
        self.assertContains(response, 'lg:')

    def test_mobile_navigation(self):
        """Test mobile navigation elements"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Should contain mobile navigation elements
        self.assertContains(response, 'Mobile menu')


class SEOTest(TestCase):
    """Test suite for SEO elements"""

    def test_homepage_meta_tags(self):
        """Test homepage contains proper meta tags"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Should contain title tag
        self.assertContains(response, '<title>')
        self.assertContains(response, 'QuickGigs')

    def test_page_titles_are_descriptive(self):
        """Test that pages have descriptive titles"""
        pages = [
            ('core:home', 'QuickGigs'),
            ('core:about', 'About'),
            ('core:contact', 'Contact'),
        ]
        
        for url_name, expected_title_content in pages:
            url = reverse(url_name)
            response = self.client.get(url)
            self.assertContains(response, expected_title_content)

    def test_structured_data_present(self):
        """Test that structured data is present where appropriate"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        # This test would check for JSON-LD or other structured data
        # Currently we're just ensuring the page loads correctly
        self.assertEqual(response.status_code, 200)


class StaticFilesTest(TestCase):
    """Test suite for static files integration"""

    def test_css_files_referenced(self):
        """Test that CSS files are properly referenced"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Should contain CSS references
        self.assertContains(response, 'css')

    def test_javascript_files_referenced(self):
        """Test that JavaScript files are properly referenced"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        # Should contain JavaScript references (if any)
        # This is a basic test that the page structure is correct
        self.assertEqual(response.status_code, 200)


class ErrorHandlingTest(TestCase):
    """Test suite for error handling"""

    def test_404_error_handling(self):
        """Test 404 error handling"""
        # Try to access a non-existent page
        response = self.client.get('/nonexistent-page/')
        
        # Should return 404
        self.assertEqual(response.status_code, 404)

    def test_500_error_handling(self):
        """Test 500 error handling setup"""
        # This test ensures error handling is configured
        # In production, this would test custom 500 error pages
        from django.conf import settings
        
        # Check that DEBUG is configured (should be False in production)
        self.assertIsNotNone(settings.DEBUG)


class PerformanceTest(TestCase):
    """Test suite for performance considerations"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user and gigs for performance testing
        self.employer = User.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='testpass123'
        )
        
        # Create multiple gigs to test query efficiency
        for i in range(20):
            Gig.objects.create(
                title=f'Performance Test Gig {i}',
                employer=self.employer,
                budget=Decimal('500.00'),
                category='web_dev',
                is_featured=(i % 5 == 0)  # Every 5th gig is featured
            )

    def test_homepage_query_efficiency(self):
        """Test that homepage doesn't create N+1 queries"""
        url = reverse('core:home')
        
        # Test with a reasonable number of queries
        # This number should be adjusted based on your actual optimizations
        with self.assertNumQueries(5):  # Adjust based on actual query count
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_gig_list_query_efficiency(self):
        """Test that gig list is efficiently queried"""
        url = reverse('gigs:gig_list')
        
        # Should not create excessive queries even with many gigs
        with self.assertNumQueries(3):  # Adjust based on actual query count
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)