from django.contrib import admin
from .models import StudentExtra, Book, IssuedBook


@admin.register(StudentExtra)
class StudentExtraAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'enrollment', 'branch']
    # FIX: get_name is a property, not a db field — can't search_fields on it directly
    search_fields = ['user__first_name', 'user__last_name', 'user__username', 'enrollment']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['name', 'isbn', 'author', 'category']
    list_filter = ['category']
    search_fields = ['name', 'author']  # FIX: isbn is IntegerField, exclude from search_fields


@admin.register(IssuedBook)
class IssuedBookAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'isbn', 'issuedate', 'expirydate', 'status']
    list_filter = ['status']
    search_fields = ['enrollment', 'isbn']
