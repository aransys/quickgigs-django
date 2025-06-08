# QuickGigs Transformation Plan

## Overview

Transforming existing todo application into a micro job board platform while maintaining code quality and testing standards.

## Database Schema Evolution

### Current Models (Todo App)

- **Task Model**: title, description, completed, due_date, user
- **User Model**: Django's built-in User

### Target Models (QuickGigs)

#### 1. Gig (evolved from Task)

```python
class Gig(models.Model):
    # Evolved from Task model
    title = models.CharField(max_length=200)           # Keep
    description = models.TextField()                   # Keep
    created_at = models.DateTimeField(auto_now_add=True)  # Keep

    # Transform existing fields
    deadline = models.DateField(null=True, blank=True)  # Was: due_date
    is_active = models.BooleanField(default=True)       # Was: completed (inverse)

    # New fields
    employer = models.ForeignKey(User, on_delete=models.CASCADE)
    budget = models.DecimalField(max_digits=8, decimal_places=2)
    location = models.CharField(max_length=100, default='Remote')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    is_featured = models.BooleanField(default=False)
```
