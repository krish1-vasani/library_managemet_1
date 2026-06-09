from django import forms
from django.contrib.auth.models import User
from . import models


class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500, widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))


class StudentUserForm(forms.ModelForm):
    """
    FIX: Use PasswordInput widget so the password is masked in the browser.
    The password field is kept as plain CharField here — hashing is done
    explicitly in studentsignup_view via user.set_password().
    """
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']


class StudentExtraForm(forms.ModelForm):
    class Meta:
        model = models.StudentExtra
        fields = ['enrollment', 'branch']


class BookForm(forms.ModelForm):
    class Meta:
        model = models.Book
        fields = ['name', 'isbn', 'author', 'category']


class IssuedBookForm(forms.Form):
    """
    FIX: ModelChoiceField returns model instances; the view must read
    .isbn and .enrollment from the returned objects (not raw POST strings).
    This form is correct — the fix is in issuebook_view which now uses
    form.cleaned_data['isbn2'].isbn instead of request.POST.get('isbn2').
    """
    isbn2 = forms.ModelChoiceField(
        queryset=models.Book.objects.all(),
        empty_label="-- Select Book (Name and ISBN) --",
        to_field_name="isbn",
        label='Name and ISBN',
    )
    enrollment2 = forms.ModelChoiceField(
        queryset=models.StudentExtra.objects.all(),
        empty_label="-- Select Student (Name and Enrollment) --",
        to_field_name='enrollment',
        label='Name and Enrollment',
    )
