from django.db import models
from django.utils import timezone


class Task(models.Model):
    # Field definitions
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)

    # Methods
    def __str__(self):
        return self.title

    def is_overdue(self):
        """
        Check if task is past its due date and not completed.

        Returns:
            bool: True if task is overdue, False otherwise
        """
        if self.due_date and not self.completed:
            return self.due_date < timezone.now().date()
        return False

    # Meta class
    class Meta:
        ordering = ["completed", "due_date", "created_at"]
        # Show incomplete tasks first, then by due date, then by creation

        verbose_name = "Task"
        verbose_name_plural = "Tasks"
