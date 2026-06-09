from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta


class StudentExtra(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    enrollment = models.CharField(max_length=40)
    branch = models.CharField(max_length=40)

    def __str__(self):
        return self.user.first_name + ' [' + str(self.enrollment) + ']'

    @property
    def get_name(self):
        # FIX: return full name if available, otherwise username
        full_name = self.user.get_full_name()
        return full_name if full_name.strip() else self.user.username

    @property
    def getuserid(self):
        return self.user.id


class Book(models.Model):
    CATEGORY_CHOICES = [
        ('education', 'Education'),
        ('entertainment', 'Entertainment'),
        ('comics', 'Comics'),
        ('biography', 'Biography'),
        ('history', 'History'),
    ]
    name = models.CharField(max_length=30)
    # FIX: isbn as PositiveIntegerField is fine but store as str in IssuedBook —
    # keep consistent. No change needed here; the filter in views uses str(isbn).
    isbn = models.PositiveIntegerField()
    author = models.CharField(max_length=40)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='education')

    def __str__(self):
        return str(self.name) + ' [' + str(self.isbn) + ']'


def get_expiry():
    """Return a date 15 days from today. Used as default for IssuedBook.expirydate."""
    return datetime.today() + timedelta(days=15)


class IssuedBook(models.Model):
    STATUS_CHOICES = [
        ('Issued', 'Issued'),
        ('Returned', 'Returned'),
    ]
    enrollment = models.CharField(max_length=30)
    isbn = models.CharField(max_length=30)  # stored as string to match Book.isbn via filter
    issuedate = models.DateField(auto_now=True)
    expirydate = models.DateField(default=get_expiry)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Issued')

    def __str__(self):
        return self.enrollment
