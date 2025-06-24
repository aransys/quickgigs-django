from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import get_user
from accounts.models import UserProfile
from accounts.forms import SignUpForm


class AuthenticationViewTest(TestCase):
    """Test suite for authentication views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        
        self.existing_user = User.objects.create_user(
            username='existing',
            email='existing@test.com',
            password='testpass123'
        )

    def test_signup_page_loads(self):
        """Test signup page loads correctly"""
        url = reverse('accounts:signup')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign Up')
        self.assertContains(response, 'form')

    def test_successful_user_registration(self):
        """Test successful user registration flow"""
        url = reverse('accounts:signup')
        response = self.client.post(url, self.user_data)
        
        # Should redirect to role selection
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/choose-role/', response.url)
        
        # User should be created and logged in
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')
        
        # User should be logged in automatically
        logged_in_user = get_user(self.client)
        self.assertTrue(logged_in_user.is_authenticated)
        self.assertEqual(logged_in_user, user)

    def test_registration_with_invalid_data(self):
        """Test registration with invalid form data"""
        invalid_data = self.user_data.copy()
        invalid_data['password2'] = 'differentpassword'
        
        url = reverse('accounts:signup')
        response = self.client.post(url, invalid_data)
        
        # Should not redirect (form errors)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error')
        
        # User should not be created
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_registration_with_existing_username(self):
        """Test registration with already existing username"""
        invalid_data = self.user_data.copy()
        invalid_data['username'] = 'existing'
        
        url = reverse('accounts:signup')
        response = self.client.post(url, invalid_data)
        
        # Should show form errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')

    def test_login_page_loads(self):
        """Test login page loads correctly"""
        url = reverse('accounts:login')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Username')
        self.assertContains(response, 'Password')

    def test_successful_login(self):
        """Test successful user login"""
        url = reverse('accounts:login')
        login_data = {
            'username': 'existing',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, login_data)
        
        # Should redirect to homepage
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/gigs/')
        
        # User should be logged in
        logged_in_user = get_user(self.client)
        self.assertTrue(logged_in_user.is_authenticated)
        self.assertEqual(logged_in_user, self.existing_user)

    def test_login_with_invalid_credentials(self):
        """Test login with wrong credentials"""
        url = reverse('accounts:login')
        invalid_data = {
            'username': 'existing',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, invalid_data)
        
        # Should not redirect
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please check your username and password and try again.')
        
        # User should not be logged in
        logged_in_user = get_user(self.client)
        self.assertFalse(logged_in_user.is_authenticated)

    def test_logout_functionality(self):
        """Test user logout"""
        # Login first
        self.client.login(username='existing', password='testpass123')
        
        # Verify logged in
        logged_in_user = get_user(self.client)
        self.assertTrue(logged_in_user.is_authenticated)
        
        # Logout
        url = reverse('accounts:logout')
        response = self.client.post(url)
        
        # Should redirect to homepage
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/gigs/')
        
        # User should be logged out
        logged_in_user = get_user(self.client)
        self.assertFalse(logged_in_user.is_authenticated)


class RoleSelectionViewTest(TestCase):
    """Test suite for role selection functionality"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

    def test_choose_role_requires_login(self):
        """Test that role selection requires authentication"""
        url = reverse('accounts:choose_role')
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_choose_role_page_loads(self):
        """Test role selection page loads for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('accounts:choose_role')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Choose Your Role')
        self.assertContains(response, 'Employer')
        self.assertContains(response, 'Freelancer')

    def test_employer_role_selection(self):
        """Test selecting employer role"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('accounts:choose_role')
        response = self.client.post(url, {'role': 'employer'})
        
        # Should redirect to gigs page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/gigs/')
        
        # User profile should be updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.userprofile.user_type, 'employer')

    def test_freelancer_role_selection(self):
        """Test selecting freelancer role"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('accounts:choose_role')
        response = self.client.post(url, {'role': 'freelancer'})
        
        # Should redirect to homepage
        self.assertEqual(response.status_code, 302)
        
        # User profile should be updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.userprofile.user_type, 'freelancer')

    def test_invalid_role_selection(self):
        """Test submitting invalid role"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('accounts:choose_role')
        response = self.client.post(url, {'role': 'invalid'})
        
        # Should not redirect (invalid data)
        self.assertEqual(response.status_code, 200)
        
        # User profile should not be changed
        self.user.refresh_from_db()
        self.assertEqual(self.user.userprofile.user_type, 'freelancer')  # Default


class ProfileViewTest(TestCase):
    """Test suite for profile views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        # Set up profile data
        profile = self.user.userprofile
        profile.user_type = 'freelancer'
        profile.bio = 'Experienced developer'
        profile.skills = 'Python, Django, JavaScript'
        profile.hourly_rate = 75.00
        profile.save()

    def test_profile_view_requires_login(self):
        """Test that profile view requires authentication"""
        url = reverse('accounts:profile')
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_profile_view_loads(self):
        """Test profile view loads correctly"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('accounts:profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'Experienced developer')
        self.assertContains(response, 'Python')
        self.assertContains(response, 'Django')

    def test_profile_edit_view_requires_login(self):
        """Test that profile edit requires authentication"""
        url = reverse('accounts:profile_edit')
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_profile_edit_view_loads(self):
        """Test profile edit view loads correctly"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('accounts:profile_edit')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Profile')
        self.assertContains(response, 'form')

    def test_profile_update(self):
        """Test updating profile information"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('accounts:profile_edit')
        update_data = {
            'bio': 'Updated bio text',
            'skills': 'Python, Django, React, Vue.js',
            'hourly_rate': '85.00',
            'phone': '555-0123'
        }
        
        response = self.client.post(url, update_data)
        
        # Should redirect to profile view
        self.assertEqual(response.status_code, 302)
        
        # Profile should be updated
        self.user.refresh_from_db()
        profile = self.user.userprofile
        self.assertEqual(profile.bio, 'Updated bio text')
        self.assertEqual(profile.skills, 'Python, Django, React, Vue.js')
        self.assertEqual(float(profile.hourly_rate), 85.00)
        self.assertEqual(profile.phone, '555-0123')


class UserNavigationTest(TestCase):
    """Test suite for user navigation and UI elements"""

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

    def test_anonymous_user_navigation(self):
        """Test navigation for anonymous users"""
        url = reverse('core:home')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Sign Up')
        self.assertNotContains(response, 'Profile')
        self.assertNotContains(response, 'Logout')

    def test_employer_navigation(self):
        """Test navigation for employer users"""
        self.client.login(username='employer', password='testpass123')
        
        url = reverse('core:home')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'employer')  # Username in nav
        self.assertContains(response, 'Profile')
        self.assertContains(response, 'Logout')
        self.assertNotContains(response, 'Login')
        self.assertNotContains(response, 'Sign Up')

    def test_freelancer_navigation(self):
        """Test navigation for freelancer users"""
        self.client.login(username='freelancer', password='testpass123')
        
        url = reverse('core:home')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'freelancer')  # Username in nav
        self.assertContains(response, 'Profile')
        self.assertContains(response, 'Logout')


class SecurityTest(TestCase):
    """Test suite for authentication security"""

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

    def test_profile_privacy(self):
        """Test that users can only access their own profile edit"""
        # Login as user1
        self.client.login(username='user1', password='testpass123')
        
        # Try to access own profile edit
        url = reverse('accounts:profile_edit')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_csrf_protection(self):
        """Test CSRF protection on forms"""
        # Create a client that enforces CSRF checks
        from django.test import Client
        csrf_client = Client(enforce_csrf_checks=True)
        
        # Attempt to post without CSRF token should fail
        url = reverse('accounts:signup')
        response = csrf_client.post(url, {
            'username': 'testuser',
            'email': 'test@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        
        # Should be rejected due to missing CSRF token
        self.assertEqual(response.status_code, 403)