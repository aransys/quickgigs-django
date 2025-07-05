from django.test import TestCase
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from decimal import Decimal

from .models import UserProfile


class UserProfileModelTest(TestCase):
    """Test UserProfile model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_profile_auto_creation(self):
        """Test that UserProfile is automatically created with User"""
        # Profile should be created automatically via signals
        self.assertTrue(hasattr(self.user, 'userprofile'))
        self.assertIsInstance(self.user.userprofile, UserProfile)
    
    def test_user_profile_default_values(self):
        """Test default UserProfile values"""
        profile = self.user.userprofile
        
        self.assertEqual(profile.user_type, 'freelancer')  # FIXED FOR GREEN PHASE
        self.assertEqual(profile.bio, '')
        self.assertEqual(profile.skills, '')
        self.assertIsNone(profile.hourly_rate)
        self.assertEqual(profile.company_name, '')
        self.assertEqual(profile.phone, '')
        self.assertIsNotNone(profile.created_at)
    
    def test_user_profile_employer_setup(self):
        """Test employer profile configuration"""
        profile = self.user.userprofile
        profile.user_type = 'employer'
        profile.company_name = 'Test Company Ltd'
        profile.bio = 'We are a leading tech company'
        profile.phone = '+1-555-123-4567'
        profile.save()
        
        self.assertEqual(profile.user_type, 'employer')
        self.assertEqual(profile.company_name, 'Test Company Ltd')
        self.assertTrue(profile.is_employer)
        self.assertFalse(profile.is_freelancer)
    
    def test_user_profile_freelancer_setup(self):
        """Test freelancer profile configuration"""
        profile = self.user.userprofile
        profile.user_type = 'freelancer'
        profile.skills = 'Python, Django, JavaScript, React'
        profile.hourly_rate = Decimal('75.00')
        profile.bio = 'Experienced full-stack developer'
        profile.save()
        
        self.assertEqual(profile.user_type, 'freelancer')
        self.assertEqual(profile.hourly_rate, Decimal('75.00'))
        self.assertTrue(profile.is_freelancer)
        self.assertFalse(profile.is_employer)
    
    def test_user_profile_property_methods(self):
        """Test UserProfile property methods"""
        profile = self.user.userprofile
        
        # Test freelancer properties
        profile.user_type = 'freelancer'
        profile.save()
        self.assertTrue(profile.is_freelancer)
        self.assertFalse(profile.is_employer)
        
        # Test employer properties
        profile.user_type = 'employer'
        profile.save()
        self.assertTrue(profile.is_employer)
        self.assertFalse(profile.is_freelancer)
    
    def test_user_profile_one_to_one_relationship(self):
        """Test UserProfile one-to-one relationship with User"""
        profile = self.user.userprofile
        
        # Profile should reference the correct user
        self.assertEqual(profile.user, self.user)
        
        # User should have only one profile
        self.assertEqual(UserProfile.objects.filter(user=self.user).count(), 1)
    
    def test_user_profile_string_representation(self):
        """Test UserProfile string representation"""
        profile = self.user.userprofile
        expected_str = f"{self.user.username} - Freelancer"
        self.assertEqual(str(profile), expected_str)
        
        # Test with employer
        profile.user_type = 'employer'
        profile.save()
        expected_str = f"{self.user.username} - Employer"
        self.assertEqual(str(profile), expected_str)
    
    def test_skills_processing(self):
        """Test skills field functionality"""
        profile = self.user.userprofile
        
        # Test skills with various formats
        skills_tests = [
            'Python, Django, JavaScript',
            'Python,Django,JavaScript',
            'Python , Django , JavaScript ',
            'Python'
        ]
        
        for skills in skills_tests:
            profile.skills = skills
            profile.save()
            # In real template, this would be processed as skills_list
            self.assertIsInstance(profile.skills, str)
    
    def test_hourly_rate_validation(self):
        """Test hourly rate field validation"""
        profile = self.user.userprofile
        
        # Valid rates
        valid_rates = [Decimal('50.00'), Decimal('100.50'), Decimal('25.75')]
        for rate in valid_rates:
            profile.hourly_rate = rate
            profile.save()
            self.assertEqual(profile.hourly_rate, rate)
        
        # Null rate should be allowed
        profile.hourly_rate = None
        profile.save()
        self.assertIsNone(profile.hourly_rate)
    
    def test_user_profile_cascade_deletion(self):
        """Test profile deletion when user is deleted"""
        profile_id = self.user.userprofile.id
        
        # Delete user
        self.user.delete()
        
        # Profile should also be deleted (CASCADE)
        with self.assertRaises(UserProfile.DoesNotExist):
            UserProfile.objects.get(id=profile_id)
    
    def test_user_type_choices(self):
        """Test user_type field choices"""
        profile = self.user.userprofile
        
        # Valid choices
        valid_types = ['employer', 'freelancer']
        for user_type in valid_types:
            profile.user_type = user_type
            profile.save()
            self.assertEqual(profile.user_type, user_type)


class UserProfileSignalTest(TestCase):
    """Test UserProfile signal-based creation"""
    
    def test_profile_created_on_user_creation(self):
        """Test that profile is created when user is created"""
        # Create new user
        new_user = User.objects.create_user(
            username='signaltest',
            email='signal@example.com',
            password='testpass123'
        )
        
        # Profile should exist immediately
        self.assertTrue(hasattr(new_user, 'userprofile'))
        self.assertEqual(new_user.userprofile.user, new_user)
        self.assertEqual(new_user.userprofile.user_type, 'freelancer')
    
    def test_profile_saved_on_user_save(self):
        """Test that profile is saved when user is saved"""
        user = User.objects.create_user(
            username='savetest',
            email='save@example.com',
            password='testpass123'
        )
        
        # Modify profile
        user.userprofile.bio = 'Updated bio'
        
        # Save user (should trigger profile save)
        user.save()
        
        # Reload from database
        user.refresh_from_db()
        self.assertEqual(user.userprofile.bio, 'Updated bio')