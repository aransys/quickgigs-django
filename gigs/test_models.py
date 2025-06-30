from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from decimal import Decimal

from .models import Gig


class GigModelTest(TestCase):
    """Test Gig model functionality and business logic"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testemployer',
            email='test@example.com',
            password='testpass123'
        )
        
        self.gig_data = {
            'title': 'Test Web Development Project',
            'description': 'Build a Django application for testing',
            'employer': self.user,
            'budget': Decimal('500.00'),
            'location': 'Remote',
            'category': 'web_dev',
            'deadline': date.today() + timedelta(days=30)
        }
    
    def test_gig_creation(self):
        """Test basic gig creation"""
        gig = Gig.objects.create(**self.gig_data)
        
        self.assertEqual(gig.title, 'Test Web Development Project')
        self.assertEqual(gig.employer, self.user)
        self.assertEqual(gig.budget, Decimal('500.00'))
        self.assertEqual(gig.category, 'web_dev')
        self.assertTrue(gig.is_active)
        self.assertFalse(gig.is_featured)
    
    def test_gig_string_representation(self):
        """Test gig __str__ method"""
        gig = Gig.objects.create(**self.gig_data)
        self.assertEqual(str(gig), 'Test Web Development Project')
    
    def test_gig_is_overdue_method(self):
        """Test is_overdue business logic"""
        # Future deadline - not overdue
        future_gig = Gig.objects.create(**self.gig_data)
        self.assertFalse(future_gig.is_overdue())
        
        # Past deadline and active - overdue
        past_deadline = self.gig_data.copy()
        past_deadline['deadline'] = date.today() - timedelta(days=1)
        past_gig = Gig.objects.create(**past_deadline)
        self.assertTrue(past_gig.is_overdue())
        
        # Past deadline but inactive - not overdue
        past_gig.is_active = False
        past_gig.save()
        self.assertFalse(past_gig.is_overdue())
    
    def test_gig_is_available_method(self):
        """Test is_available business logic"""
        gig = Gig.objects.create(**self.gig_data)
        
        # Active gig should be available
        self.assertTrue(gig.is_available())
        
        # Inactive gig should not be available
        gig.is_active = False
        gig.save()
        self.assertFalse(gig.is_available())
        
        # Past deadline gig should not be available
        gig.is_active = True
        gig.deadline = date.today() - timedelta(days=1)
        gig.save()
        self.assertFalse(gig.is_available())
    
    def test_gig_category_choices(self):
        """Test category validation"""
        valid_categories = [
            'web_dev', 'design', 'writing', 'marketing', 
            'data_entry', 'admin', 'tech_support', 'other'
        ]
        
        for category in valid_categories:
            gig_data = self.gig_data.copy()
            gig_data['category'] = category
            gig = Gig.objects.create(**gig_data)
            self.assertEqual(gig.category, category)
    
    def test_gig_ordering(self):
        """Test default gig ordering"""
        # Create regular gig
        regular_gig = Gig.objects.create(**self.gig_data)
        
        # Create featured gig
        featured_data = self.gig_data.copy()
        featured_data['title'] = 'Featured Test Project'
        featured_data['is_featured'] = True
        featured_gig = Gig.objects.create(**featured_data)
        
        # Featured gigs should come first
        gigs = list(Gig.objects.all())
        self.assertEqual(gigs[0], featured_gig)
        self.assertEqual(gigs[1], regular_gig)
    
    def test_gig_budget_validation(self):
        """Test budget field validation"""
        # Valid budget
        gig = Gig.objects.create(**self.gig_data)
        self.assertEqual(gig.budget, Decimal('500.00'))
        
        # Zero budget should be allowed
        zero_budget_data = self.gig_data.copy()
        zero_budget_data['budget'] = Decimal('0.00')
        zero_gig = Gig.objects.create(**zero_budget_data)
        self.assertEqual(zero_gig.budget, Decimal('0.00'))

# class TaskModelTest(TestCase):
#     ... (comment out the entire class and its methods)

#     def setUp(self):
#         """Set up test data"""
#         self.task_data = {
#             'title': 'Test Task',
#             'description': 'Complete testing implementation',
#             'due_date': date.today() + timedelta(days=7)
#         }
#     
#     def test_task_creation(self):
#         """Test basic task creation"""
#         task = Task.objects.create(**self.task_data)
#         
#         self.assertEqual(task.title, 'Test Task')
#         self.assertFalse(task.completed)
#         self.assertIsNotNone(task.created_at)
#     
#     def test_task_completion(self):
#         """Test task completion functionality"""
#         task = Task.objects.create(**self.task_data)
#         
#         # Initially not completed
#         self.assertFalse(task.completed)
#         
#         # Mark as completed
#         task.completed = True
#         task.save()
#         self.assertTrue(task.completed)
#     
#     def test_task_is_overdue(self):
#         """Test task overdue logic"""
#         # Future due date - not overdue
#         future_task = Task.objects.create(**self.task_data)
#         self.assertFalse(future_task.is_overdue())
#         
#         # Past due date and not completed - overdue
#         past_data = self.task_data.copy()
#         past_data['due_date'] = date.today() - timedelta(days=1)
#         past_task = Task.objects.create(**past_data)
#         self.assertTrue(past_task.is_overdue())
#         
#         # Past due date but completed - not overdue
#         past_task.completed = True
#         past_task.save()
#         self.assertFalse(past_task.is_overdue())
#         
#         # No due date - not overdue
#         no_date_data = self.task_data.copy()
#         no_date_data['due_date'] = None
#         no_date_task = Task.objects.create(**no_date_data)
#         self.assertFalse(no_date_task.is_overdue())
#     
#     def test_task_ordering(self):
#         """Test task default ordering"""
#         # Create completed task
#         completed_data = self.task_data.copy()
#         completed_data['title'] = 'Completed Task'
#         completed_data['completed'] = True
#         completed_task = Task.objects.create(**completed_data)
#         
#         # Create pending task
#         pending_task = Task.objects.create(**self.task_data)
#         
#         # Pending tasks should come before completed
#         tasks = list(Task.objects.all())
#         self.assertEqual(tasks[0], pending_task)
#         self.assertEqual(tasks[1], completed_task)  