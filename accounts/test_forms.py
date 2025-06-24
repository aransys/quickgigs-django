from django.test import TestCase
from django.contrib.auth.models import User
from accounts.forms import SignUpForm, UserProfileForm
from decimal import Decimal


class SignUpFormTest(TestCase):
    """Test suite for user registration form"""

    def setUp(self):
        """Set up test data"""
        self.valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }

    def test_valid_signup_form(self):
        """Test form with valid data"""
        form = SignUpForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_signup_form_saves_user(self):
        """Test that form saves user correctly"""
        form = SignUpForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))

    def test_signup_form_password_mismatch(self):
        """Test form with mismatched passwords"""
        form_data = self.valid_data.copy()
        form_data['password2'] = 'differentpass'
        
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_signup_form_missing_email(self):
        """Test form without email"""
        form_data = self.valid_data.copy()
        del form_data['email']
        
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_signup_form_invalid_email(self):
        """Test form with invalid email format"""
        form_data = self.valid_data.copy()
        form_data['email'] = 'invalid-email'
        
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_signup_form_weak_password(self):
        """Test form with weak password"""
        form_data = self.valid_data.copy()
        form_data['password1'] = '123'
        form_data['password2'] = '123'
        
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_signup_form_existing_username(self):
        """Test form with already existing username"""
        # Create existing user
        User.objects.create_user(
            username='testuser',
            email='existing@test.com',
            password='testpass123'
        )
        
        form = SignUpForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_signup_form_widget_classes(self):
        """Test that form widgets have correct CSS classes"""
        form = SignUpForm()
        
        # Check that widgets have Tailwind CSS classes
        username_widget = form.fields['username'].widget
        email_widget = form.fields['email'].widget
        
        self.assertIn('w-full', username_widget.attrs['class'])
        self.assertIn('px-4', username_widget.attrs['class'])
        self.assertIn('border', username_widget.attrs['class'])
        
        self.assertIn('w-full', email_widget.attrs['class'])
        self.assertIn('px-4', email_widget.attrs['class'])

    def test_signup_form_placeholders(self):
        """Test form field placeholders"""
        form = SignUpForm()
        
        self.assertEqual(
            form.fields['username'].widget.attrs['placeholder'],
            'Choose a username'
        )
        self.assertEqual(
            form.fields['email'].widget.attrs['placeholder'],
            'Enter your email address'
        )

    def test_signup_form_empty_data(self):
        """Test form with empty data"""
        form = SignUpForm(data={})
        
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password1', form.errors)
        self.assertIn('password2', form.errors)


class UserProfileFormTest(TestCase):
    """Test suite for profile update form"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        self.valid_data = {
            'bio': 'Experienced web developer',
            'skills': 'Python, Django, JavaScript',
            'hourly_rate': '75.50',
            'company_name': 'Tech Solutions',
            'phone': '555-0123'
        }

    def test_valid_profile_form(self):
        """Test form with valid data"""
        form = UserProfileForm(
            data=self.valid_data,
            instance=self.user.userprofile
        )
        self.assertTrue(form.is_valid())

    def test_profile_form_saves_data(self):
        """Test that form saves profile data correctly"""
        form = UserProfileForm(
            data=self.valid_data,
            instance=self.user.userprofile
        )
        self.assertTrue(form.is_valid())
        
        profile = form.save()
        self.assertEqual(profile.bio, 'Experienced web developer')
        self.assertEqual(profile.skills, 'Python, Django, JavaScript')
        self.assertEqual(profile.hourly_rate, Decimal('75.50'))
        self.assertEqual(profile.company_name, 'Tech Solutions')
        self.assertEqual(profile.phone, '555-0123')

    def test_profile_form_empty_optional_fields(self):
        """Test form with empty optional fields"""
        minimal_data = {
            'bio': '',
            'skills': '',
            'hourly_rate': '',
            'company_name': '',
            'phone': ''
        }
        
        form = UserProfileForm(
            data=minimal_data,
            instance=self.user.userprofile
        )
        self.assertTrue(form.is_valid())

    def test_profile_form_invalid_hourly_rate(self):
        """Test form with invalid hourly rate"""
        form_data = self.valid_data.copy()
        form_data['hourly_rate'] = 'invalid'
        
        form = UserProfileForm(
            data=form_data,
            instance=self.user.userprofile
        )
        self.assertFalse(form.is_valid())
        self.assertIn('hourly_rate', form.errors)

    def test_profile_form_negative_hourly_rate(self):
        """Test form with negative hourly rate"""
        form_data = self.valid_data.copy()
        form_data['hourly_rate'] = '-10.00'
        
        form = UserProfileForm(
            data=form_data,
            instance=self.user.userprofile
        )
        # Note: This depends on your model validation
        # You might want to add MinValueValidator to the model
        self.assertTrue(form.is_valid())  # Currently allows negative values

    def test_profile_form_very_high_hourly_rate(self):
        """Test form with very high hourly rate"""
        form_data = self.valid_data.copy()
        form_data['hourly_rate'] = '9999.99'
        
        form = UserProfileForm(
            data=form_data,
            instance=self.user.userprofile
        )
        self.assertTrue(form.is_valid())

    def test_profile_form_long_bio(self):
        """Test form with very long bio"""
        form_data = self.valid_data.copy()
        form_data['bio'] = 'A' * 1000  # Very long bio
        
        form = UserProfileForm(
            data=form_data,
            instance=self.user.userprofile
        )
        self.assertTrue(form.is_valid())  # TextField should accept long text

    def test_profile_form_special_characters_in_skills(self):
        """Test form with special characters in skills"""
        form_data = self.valid_data.copy()
        form_data['skills'] = 'Python, Django, C++, C#, Node.js, Vue.js'
        
        form = UserProfileForm(
            data=form_data,
            instance=self.user.userprofile
        )
        self.assertTrue(form.is_valid())

    def test_profile_form_phone_number_formats(self):
        """Test various phone number formats"""
        valid_phones = [
            '555-0123',
            '(555) 123-4567',
            '+1-555-123-4567',
            '555.123.4567',
            '5551234567'
        ]
        
        for phone in valid_phones:
            form_data = self.valid_data.copy()
            form_data['phone'] = phone
            
            form = UserProfileForm(
                data=form_data,
                instance=self.user.userprofile
            )
            self.assertTrue(form.is_valid(), f"Phone format {phone} should be valid")

    def test_profile_form_widget_classes(self):
        """Test that form widgets have correct CSS classes"""
        form = UserProfileForm(instance=self.user.userprofile)
        
        # Check that textarea widgets have correct classes
        bio_widget = form.fields['bio'].widget
        skills_widget = form.fields['skills'].widget
        
        self.assertIn('w-full', bio_widget.attrs['class'])
        self.assertIn('px-4', bio_widget.attrs['class'])
        self.assertIn('border', bio_widget.attrs['class'])

    def test_profile_form_help_texts(self):
        """Test form field help texts"""
        form = UserProfileForm(instance=self.user.userprofile)
        
        self.assertEqual(
            form.fields['bio'].help_text,
            'Tell us about yourself'
        )
        self.assertEqual(
            form.fields['skills'].help_text,
            'Comma-separated skills (e.g., Python, Django, JavaScript)'
        )

    def test_profile_form_placeholders(self):
        """Test form field placeholders"""
        form = UserProfileForm(instance=self.user.userprofile)
        
        self.assertIn('placeholder', form.fields['bio'].widget.attrs)
        self.assertIn('placeholder', form.fields['skills'].widget.attrs)
        self.assertIn('placeholder', form.fields['hourly_rate'].widget.attrs)

    def test_profile_form_partial_update(self):
        """Test updating only some fields"""
        # Set initial data
        profile = self.user.userprofile
        profile.bio = 'Original bio'
        profile.skills = 'Original skills'
        profile.save()
        
        # Update only bio
        partial_data = {
            'bio': 'Updated bio',
            'skills': 'Original skills',  # Keep existing
            'hourly_rate': '',
            'company_name': '',
            'phone': ''
        }
        
        form = UserProfileForm(
            data=partial_data,
            instance=profile
        )
        self.assertTrue(form.is_valid())
        
        updated_profile = form.save()
        self.assertEqual(updated_profile.bio, 'Updated bio')
        self.assertEqual(updated_profile.skills, 'Original skills')


class FormIntegrationTest(TestCase):
    """Test suite for form integration with views"""

    def test_signup_form_integration(self):
        """Test signup form works with signup view"""
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        url = reverse('accounts:signup')
        
        form_data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        
        response = client.post(url, form_data)
        
        # Should redirect (successful signup)
        self.assertEqual(response.status_code, 302)
        
        # User should be created
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'new@test.com')

    def test_profile_form_integration(self):
        """Test profile form works with profile edit view"""
        from django.test import Client
        from django.urls import reverse
        
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        client = Client()
        client.login(username='testuser', password='testpass123')
        
        url = reverse('accounts:profile_edit')
        form_data = {
            'bio': 'Updated via integration test',
            'skills': 'Integration, Testing',
            'hourly_rate': '100.00',
            'company_name': '',
            'phone': ''
        }
        
        response = client.post(url, form_data)
        
        # Should redirect (successful update)
        self.assertEqual(response.status_code, 302)
        
        # Profile should be updated
        user.refresh_from_db()
        self.assertEqual(user.userprofile.bio, 'Updated via integration test')
        self.assertEqual(user.userprofile.skills, 'Integration, Testing')
        self.assertEqual(user.userprofile.hourly_rate, Decimal('100.00'))