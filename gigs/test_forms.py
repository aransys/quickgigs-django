from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, timedelta
from gigs.models import Gig, Task
from django.core.exceptions import ValidationError


class ModelFormIntegrationTest(TestCase):
    """Test suite for Django's built-in ModelForm behavior"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

    def test_gig_model_field_validation(self):
        """Test that Gig model field validation works"""
        # Test that model validation catches invalid data
        
        # Valid gig should save
        valid_gig = Gig(
            title='Valid Gig',
            description='Valid description',
            employer=self.user,
            budget=Decimal('1000.00'),
            category='web_dev'
        )
        valid_gig.full_clean()  # This calls model validation
        valid_gig.save()
        
        self.assertEqual(valid_gig.title, 'Valid Gig')

    def test_gig_model_choices_validation(self):
        """Test that model choice fields are validated"""
        # Create gig with valid category
        gig = Gig(
            title='Category Test Gig',
            employer=self.user,
            budget=Decimal('500.00'),
            category='design'
        )
        gig.full_clean()
        gig.save()
        
        self.assertEqual(gig.category, 'design')

    def test_gig_model_decimal_field_validation(self):
        """Test that decimal fields are properly validated"""
        # Valid decimal
        gig = Gig(
            title='Budget Test Gig',
            employer=self.user,
            budget=Decimal('999.99'),
            category='web_dev'
        )
        gig.full_clean()
        gig.save()
        
        self.assertEqual(gig.budget, Decimal('999.99'))

    def test_gig_model_required_fields(self):
        """Test that required fields are enforced"""
        # Missing required field should fail validation
        gig = Gig(
            # Missing title (required field)
            description='Description without title',
            employer=self.user,
            budget=Decimal('500.00'),
            category='web_dev'
        )
        
        with self.assertRaises(ValidationError):
            gig.full_clean()

    def test_gig_model_category_choices(self):
        """Test that category choices are enforced"""
        valid_categories = [
            'web_dev', 'design', 'writing', 'marketing', 
            'data_entry', 'admin', 'tech_support', 'other'
        ]
        
        for category in valid_categories:
            gig = Gig(
                title=f'Test Gig for {category}',
                employer=self.user,
                budget=Decimal('500.00'),
                category=category
            )
            gig.full_clean()
            gig.save()
            self.assertEqual(gig.category, category)

    def test_gig_model_budget_precision(self):
        """Test budget field decimal precision"""
        # Test various budget amounts
        test_budgets = [
            Decimal('0.01'),
            Decimal('99.99'),
            Decimal('1000.00'),
            Decimal('99999.99')
        ]
        
        for budget in test_budgets:
            gig = Gig(
                title=f'Budget Test {budget}',
                employer=self.user,
                budget=budget,
                category='web_dev'
            )
            gig.full_clean()
            gig.save()
            self.assertEqual(gig.budget, budget)

    def test_gig_model_default_values(self):
        """Test model default values"""
        gig = Gig.objects.create(
            title='Default Values Test',
            employer=self.user,
            budget=Decimal('500.00'),
            category='web_dev'
        )
        
        # Test default values
        self.assertTrue(gig.is_active)
        self.assertFalse(gig.is_featured)
        self.assertEqual(gig.location, 'Remote')

    def test_gig_model_string_representation(self):
        """Test gig string representation"""
        gig = Gig.objects.create(
            title='String Test Gig',
            employer=self.user,
            budget=Decimal('500.00'),
            category='web_dev'
        )
        
        self.assertEqual(str(gig), 'String Test Gig')

    def test_gig_model_location_field(self):
        """Test location field accepts various formats"""
        locations = [
            'Remote',
            'London, UK',
            'New York, NY',
            'San Francisco, CA',
            'Anywhere'
        ]
        
        for location in locations:
            gig = Gig.objects.create(
                title=f'Location Test - {location}',
                employer=self.user,
                budget=Decimal('500.00'),
                category='web_dev',
                location=location
            )
            self.assertEqual(gig.location, location)

    def test_gig_model_deadline_field(self):
        """Test deadline field validation"""
        # Future deadline should be valid
        future_date = date.today() + timedelta(days=30)
        gig = Gig.objects.create(
            title='Future Deadline Gig',
            employer=self.user,
            budget=Decimal('500.00'),
            category='web_dev',
            deadline=future_date
        )
        self.assertEqual(gig.deadline, future_date)
        
        # Past deadline should still be valid (no model validation for past dates)
        past_date = date.today() - timedelta(days=30)
        past_gig = Gig.objects.create(
            title='Past Deadline Gig',
            employer=self.user,
            budget=Decimal('500.00'),
            category='web_dev',
            deadline=past_date
        )
        self.assertEqual(past_gig.deadline, past_date)


class FormIntegrationTest(TestCase):
    """Test suite for form integration with views"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

    def test_gig_creation_through_view(self):
        """Test gig creation through view form"""
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        client.login(username='testuser', password='testpass123')
        
        url = reverse('gigs:gig_create')
        form_data = {
            'title': 'View Integration Test Gig',
            'description': 'Created through view integration test',
            'budget': '750.00',
            'location': 'Test Location',
            'category': 'design',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
        }
        
        response = client.post(url, form_data)
        
        # Should redirect (successful creation)
        self.assertEqual(response.status_code, 302)
        
        # Gig should be created
        gig = Gig.objects.get(title='View Integration Test Gig')
        self.assertEqual(gig.employer, self.user)
        self.assertEqual(gig.budget, Decimal('750.00'))
        self.assertEqual(gig.category, 'design')

    def test_gig_update_through_view(self):
        """Test gig update through view form"""
        from django.test import Client
        from django.urls import reverse
        
        # Create initial gig
        gig = Gig.objects.create(
            title='Original Title',
            employer=self.user,
            budget=Decimal('500.00'),
            category='web_dev'
        )
        
        client = Client()
        client.login(username='testuser', password='testpass123')
        
        url = reverse('gigs:gig_update', kwargs={'pk': gig.pk})
        update_data = {
            'title': 'Updated Title',
            'description': 'Updated description',
            'budget': '800.00',
            'location': 'Updated Location',
            'category': 'design',
            'deadline': (date.today() + timedelta(days=45)).strftime('%Y-%m-%d')
        }
        
        response = client.post(url, update_data)
        
        # Should redirect (successful update)
        self.assertEqual(response.status_code, 302)
        
        # Gig should be updated
        gig.refresh_from_db()
        self.assertEqual(gig.title, 'Updated Title')
        self.assertEqual(gig.budget, Decimal('800.00'))
        self.assertEqual(gig.category, 'design')

    def test_invalid_form_data_handling(self):
        """Test handling of invalid form data"""
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        client.login(username='testuser', password='testpass123')
        
        url = reverse('gigs:gig_create')
        invalid_data = {
            'title': '',  # Required field empty
            'description': 'Valid description',
            'budget': 'invalid_budget',  # Invalid decimal
            'category': 'invalid_category'  # Invalid choice
        }
        
        response = client.post(url, invalid_data)
        
        # Should not redirect (form errors)
        self.assertEqual(response.status_code, 200)
        
        # Should contain error messages
        self.assertContains(response, 'This field is required')
        
        # No gig should be created
        self.assertEqual(Gig.objects.count(), 0)

    def test_form_field_validation_through_view(self):
        """Test various form field validations through views"""
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        client.login(username='testuser', password='testpass123')
        
        # Test empty title
        url = reverse('gigs:gig_create')
        response = client.post(url, {
            'title': '',
            'description': 'Test description',
            'budget': '500.00',
            'category': 'web_dev'
        })
        self.assertEqual(response.status_code, 200)  # Form error, no redirect
        
        # Test invalid budget format
        response = client.post(url, {
            'title': 'Test Gig',
            'description': 'Test description', 
            'budget': 'not_a_number',
            'category': 'web_dev'
        })
        self.assertEqual(response.status_code, 200)  # Form error, no redirect
        
        # Test invalid category
        response = client.post(url, {
            'title': 'Test Gig',
            'description': 'Test description',
            'budget': '500.00',
            'category': 'invalid_category'
        })
        self.assertEqual(response.status_code, 200)  # Form error, no redirect


class TaskFormTest(TestCase):
    """Test suite for Task model forms (legacy functionality)"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

    def test_task_model_validation(self):
        """Test Task model field validation"""
        # Valid task should save
        task = Task(
            title='Valid Task',
            description='Valid task description',
            due_date=date.today() + timedelta(days=7)
        )
        task.full_clean()
        task.save()
        
        self.assertEqual(task.title, 'Valid Task')
        self.assertFalse(task.completed)  # Default value

    def test_task_creation_through_view(self):
        """Test task creation through view"""
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        
        url = reverse('gigs:task_create')
        form_data = {
            'title': 'View Integration Task',
            'description': 'Created through view test',
            'due_date': (date.today() + timedelta(days=14)).strftime('%Y-%m-%d')
        }
        
        response = client.post(url, form_data)
        
        # Should redirect (successful creation)
        self.assertEqual(response.status_code, 302)
        
        # Task should be created
        task = Task.objects.get(title='View Integration Task')
        self.assertEqual(task.description, 'Created through view test')

    def test_task_required_fields(self):
        """Test task required field validation"""
        # Missing title should fail
        task = Task(
            description='Task without title',
            due_date=date.today() + timedelta(days=7)
        )
        
        with self.assertRaises(ValidationError):
            task.full_clean()

    def test_task_completion_toggle(self):
        """Test task completion functionality"""
        task = Task.objects.create(
            title='Completion Test Task',
            description='Test task completion'
        )
        
        # Initially not completed
        self.assertFalse(task.completed)
        
        # Toggle completion
        task.completed = True
        task.save()
        
        task.refresh_from_db()
        self.assertTrue(task.completed)


class GigFormSecurityTest(TestCase):
    """Test suite for form security considerations"""

    def setUp(self):
        """Set up test data"""
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

    def test_gig_employer_auto_assignment(self):
        """Test that gig employer is automatically assigned"""
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        client.login(username='user1', password='testpass123')
        
        url = reverse('gigs:gig_create')
        form_data = {
            'title': 'Security Test Gig',
            'description': 'Test employer assignment',
            'budget': '500.00',
            'category': 'web_dev',
            'location': 'New York',
        }
        
        response = client.post(url, form_data)
        
        # Should redirect (successful creation)
        self.assertEqual(response.status_code, 302)
        
        # Gig should be assigned to logged-in user
        gig = Gig.objects.get(title='Security Test Gig')
        self.assertEqual(gig.employer, self.user1)

    def test_gig_update_ownership_enforcement(self):
        """Test that only gig owner can update through forms"""
        from django.test import Client
        from django.urls import reverse
        
        # Create gig owned by user1
        gig = Gig.objects.create(
            title='User1 Gig',
            employer=self.user1,
            budget=Decimal('500.00'),
            category='web_dev'
        )
        
        # Try to update as user2
        client = Client()
        client.login(username='user2', password='testpass123')
        
        url = reverse('gigs:gig_update', kwargs={'pk': gig.pk})
        response = client.get(url)
        
        # Should return 404 (ownership check)
        self.assertEqual(response.status_code, 404)


# Note: This file provides comprehensive form testing for the gigs app.
# 
# Since QuickGigs uses Django's generic CreateView and UpdateView
# with model='Gig' and fields=[...], most form functionality
# is handled by Django's built-in ModelForm.
# 
# The testing focuses on:
# 1. Model validation (which affects form validation)
# 2. Form integration through views
# 3. Security considerations (ownership, auto-assignment)
# 4. Edge cases and error handling
#
# This approach ensures comprehensive coverage while working
# with Django's standard form handling patterns.