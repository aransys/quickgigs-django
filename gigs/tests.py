from django.test import TestCase

# from .models import Task
# class TaskModelTest(TestCase):
#     def test_task_creation(self):
#         """Test creating a task"""
#         task = Task.objects.create(title="Test Task", description="Test Description")
#         self.assertEqual(task.title, "Test Task")
#         self.assertFalse(task.completed)


class TaskViewTest(TestCase):
    def test_task_list_view(self):
        """Test task list view loads"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
