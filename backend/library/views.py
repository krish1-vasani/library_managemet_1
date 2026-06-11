from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from datetime import date
from django.core.mail import send_mail
from django.conf import settings
from django.db import connection
from . import forms, models
from django.contrib.auth.decorators import login_required


# ── Health Check ─────────────────────────────────────────────────────────────
@csrf_exempt
def studentlogin_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            username=username,
            password=password
        )

        print("USERNAME =", username)
        print("USER =", user)

        if user:
            login(request, user)
            return redirect('/studentafterlogin.html')

    return render(request, 'library/studentlogin.html')


@csrf_exempt
def adminlogin_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        print("ADMIN USERNAME =", username)
        print("ADMIN USER =", user)

        if user is not None and (user.is_staff or user.is_superuser):
            login(request, user)
            return redirect('/adminafterlogin.html')

    return render(request, 'library/adminlogin.html')

@login_required(login_url='/studentlogin.html')
def studentafterlogin_view(request):
    return render(request, 'library/studentafterlogin.html')


@login_required(login_url='/adminlogin.html')
def adminafterlogin_view(request):
    return render(request, 'library/adminafterlogin.html')

def logout_view(request):
    """Simple GET-based logout — no CSRF token needed, AWS-safe."""
    auth_logout(request)
    return redirect('home')



def health(request):
    """AWS ELB / Nginx health check endpoint."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "healthy", "database": "connected"})
    except Exception as e:
        return JsonResponse({"status": "unhealthy", "database": str(e)}, status=500)


# ── Role helpers ──────────────────────────────────────────────────────────────

def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)


def is_student(user):
    return user.is_authenticated and user.groups.filter(name='STUDENT').exists()


# ── Public views ──────────────────────────────────────────────────────────────

def home_view(request):
    return render(request, 'library/index.html')


def studentclick_view(request):
    return render(request, 'library/studentclick.html')


def adminclick_view(request):
    return render(request, 'library/adminclick.html')

@csrf_exempt
def adminsignup_view(request):
    """Admin accounts are created via 'python manage.py createsuperuser'.
    This view renders the signup page (UI preserved) but redirects form
    submit to Django admin for actual account creation."""
    return render(request, 'library/adminsignup.html')


def aboutus_view(request):
    return render(request, 'library/aboutus.html')


@csrf_exempt
def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name = sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            try:
                send_mail(
                    f'{name} || {email}',
                    message,
                    settings.EMAIL_HOST_USER or 'noreply@library.com',
                    [settings.EMAIL_HOST_USER or 'admin@library.com'],
                    fail_silently=True,  # FIX: don't crash if email not configured
                )
            except Exception:
                pass  # Email errors are non-fatal
            return render(request, 'library/contactussuccess.html')
    return render(request, 'library/contactus.html', {'form': sub})


# ── Auth views ────────────────────────────────────────────────────────────────
@csrf_exempt
def studentsignup_view(request):
    """
    FIX: Original code called user.set_password(user.password) AFTER form.save(),
    which re-hashes an already-plaintext password but then doesn't call save() again
    with the new hash. Result: login always fails.

    Correct approach: save the form with commit=False, hash the password, then save.
    """
    form1 = forms.StudentUserForm()
    form2 = forms.StudentExtraForm()
    mydict = {'form1': form1, 'form2': form2}

    if request.method == 'POST':
        form1 = forms.StudentUserForm(request.POST)
        form2 = forms.StudentExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            # FIX: save with commit=False so we can hash the password first
            user = form1.save(commit=False)
            user.set_password(form1.cleaned_data['password'])  # properly hash password
            user.save()

            f2 = form2.save(commit=False)
            f2.user = user
            f2.save()

            # Add to STUDENT group
            my_student_group, _ = Group.objects.get_or_create(name='STUDENT')
            my_student_group.user_set.add(user)

            return redirect('studentlogin')
        # FIX: only redirect on success; re-render with errors on failure
        mydict = {'form1': form1, 'form2': form2}

    return render(request, 'library/studentsignup.html', context=mydict)

@csrf_exempt
def afterlogin_view(request):
    """Redirect logged-in users to their role-specific dashboard."""
    if not request.user.is_authenticated:
        return redirect('home')
    if is_admin(request.user):
        return redirect('adminafterlogin')
    elif is_student(request.user):
        return redirect('studentafterlogin')
    # Fallback: unknown role → home
    return redirect('home')


# ── Admin views ───────────────────────────────────────────────────────────────

@csrf_exempt
@login_required(login_url='/adminlogin.html')
@user_passes_test(is_admin, login_url='/adminlogin.html')
def addbook_view(request):
    form = forms.BookForm()
    if request.method == 'POST':
        form = forms.BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('bookadded')
    return render(request, 'library/addbook.html', {'form': form})

@login_required(login_url='/adminlogin.html')
def bookadded_view(request):
    return render(request, 'library/bookadded.html')

@login_required(login_url='/adminlogin.html')
@user_passes_test(is_admin, login_url='/adminlogin.html')
def viewbook_view(request):
    books = models.Book.objects.all()
    return render(request, 'library/viewbook.html', {'books': books})


@csrf_exempt
@login_required(login_url='/adminlogin.html')
@user_passes_test(is_admin, login_url='/adminlogin.html')
def issuebook_view(request):
    form = forms.IssuedBookForm()
    if request.method == 'POST':
        form = forms.IssuedBookForm(request.POST)
        if form.is_valid():
            # FIX: Use form cleaned_data (validated values) instead of raw POST
            enrollment = str(form.cleaned_data['enrollment2'].enrollment)
            isbn = str(form.cleaned_data['isbn2'].isbn)
            obj = models.IssuedBook(enrollment=enrollment, isbn=isbn)
            obj.save()
            return redirect('bookissued')
    return render(request, 'library/issuebook.html', {'form': form})

def bookissued_view(request):
    return render(request, 'library/bookissued.html')

@login_required(login_url='/adminlogin.html')
@user_passes_test(is_admin, login_url='/adminlogin.html')
def viewissuedbook_view(request):
    """
    FIX: Original code tried to pair books[i] with students[i] via nested loop,
    which only worked when a student had exactly one book. Rewritten to correctly
    join each IssuedBook with its Book and Student.
    """
    issuedbooks = models.IssuedBook.objects.all()
    li = []
    for ib in issuedbooks:
        issdate = ib.issuedate.strftime('%d-%m-%Y')
        expdate = ib.expirydate.strftime('%d-%m-%Y')
        days_held = (date.today() - ib.issuedate).days
        fine = max(0, (days_held - 15) * 10)

        # Get the book (by isbn string match)
        book = models.Book.objects.filter(isbn=ib.isbn).first()
        student = models.StudentExtra.objects.filter(enrollment=ib.enrollment).first()

        if book and student:
            t = (
                student.get_name, student.enrollment,
                book.name, book.author,
                issdate, expdate, fine, ib.status
            )
            li.append(t)
        elif book:
            # Student record missing but still show book info
            t = ('Unknown', ib.enrollment, book.name, book.author, issdate, expdate, fine, ib.status)
            li.append(t)

    return render(request, 'library/viewissuedbook.html', {'li': li})


@login_required(login_url='/adminlogin.html')
@user_passes_test(is_admin, login_url='/adminlogin.html')
def viewstudent_view(request):
    students = models.StudentExtra.objects.all()
    return render(request, 'library/viewstudent.html', {'students': students})


# ── Student views ─────────────────────────────────────────────────────────────

@login_required(login_url='/studentlogin.html')
def viewissuedbookbystudent(request):
    """FIX: Guard against students with no StudentExtra profile."""
    try:
        student = models.StudentExtra.objects.get(user_id=request.user.id)
    except models.StudentExtra.DoesNotExist:
        return redirect('studentlogin')

    issuedbooks = models.IssuedBook.objects.filter(enrollment=student.enrollment)
    li1, li2 = [], []
    for ib in issuedbooks:
        book = models.Book.objects.filter(isbn=ib.isbn).first()
        if book:
            li1.append((request.user.get_full_name() or request.user.username,
                        student.enrollment, student.branch, book.name, book.author))
        issdate = ib.issuedate.strftime('%d-%m-%Y')
        expdate = ib.expirydate.strftime('%d-%m-%Y')
        days_held = (date.today() - ib.issuedate).days
        fine = max(0, (days_held - 15) * 10)
        li2.append((issdate, expdate, fine, ib.status, ib.id))

    return render(request, 'library/viewissuedbookbystudent.html', {'li1': li1, 'li2': li2})

def return_book(request, pk):
    if request.method == "POST":
        issued_book = get_object_or_404(models.IssuedBook, pk=pk)

        issued_book.status = "Returned"
        issued_book.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False}, status=405)


# ── JSON API endpoints (consumed by JS fetch() in HTML templates) ─────────────
# FIX: The frontend uses static HTML + JavaScript fetch() to load data.
#      These endpoints were missing entirely, causing all data tables to show errors.

@login_required(login_url='/adminlogin.html')
def api_books(request):
    """Return all books as JSON. Used by viewbook.html and issuebook.html."""
    books = list(models.Book.objects.values('id', 'name', 'isbn', 'author', 'category'))
    return JsonResponse(books, safe=False)


@login_required(login_url='/adminlogin.html')
def api_students(request):
    """Return all students as JSON. Used by issuebook.html and viewstudent.html."""
    students = models.StudentExtra.objects.select_related('user').all()
    data = [
        {
            'id': s.id,
            'name': s.get_name,
            'enrollment': s.enrollment,
            'branch': s.branch,
        }
        for s in students
    ]
    return JsonResponse(data, safe=False)


@login_required(login_url='/adminlogin.html')
@user_passes_test(is_admin, login_url='/adminlogin.html')
def api_issuedbooks(request):
    """Return all issued books with joined student/book info. Used by viewissuedbook.html."""
    issuedbooks = models.IssuedBook.objects.all()
    data = []
    for ib in issuedbooks:
        book = models.Book.objects.filter(isbn=ib.isbn).first()
        student = models.StudentExtra.objects.filter(enrollment=ib.enrollment).first()
        days_held = (date.today() - ib.issuedate).days
        fine = max(0, (days_held - 15) * 10)
        data.append({
            'student_name': student.get_name if student else 'Unknown',
            'enrollment': ib.enrollment,
            'book_name': book.name if book else 'Unknown',
            'book_author': book.author if book else 'Unknown',
            'issue_date': ib.issuedate.strftime('%d-%m-%Y'),
            'expiry_date': ib.expirydate.strftime('%d-%m-%Y'),
            'fine': fine,
            'status': ib.status,
        })
    return JsonResponse(data, safe=False)


@login_required(login_url='/studentlogin.html')
def api_myissuedbooks(request):
    """Return the logged-in student's issued books. Used by viewissuedbookbystudent.html."""
    try:
        student = models.StudentExtra.objects.get(user_id=request.user.id)
    except models.StudentExtra.DoesNotExist:
        return JsonResponse({'li1': [], 'li2': []})

    issuedbooks = models.IssuedBook.objects.filter(enrollment=student.enrollment)
    li1, li2 = [], []
    for ib in issuedbooks:
        book = models.Book.objects.filter(isbn=ib.isbn).first()
        if book:
            li1.append([
                request.user.get_full_name() or request.user.username,
                student.enrollment,
                student.branch,
                book.name,
                book.author,
            ])
        days_held = (date.today() - ib.issuedate).days
        fine = max(0, (days_held - 15) * 10)
        li2.append([
            ib.issuedate.strftime('%d-%m-%Y'),
            ib.expirydate.strftime('%d-%m-%Y'),
            fine,
            ib.status,
            ib.id,
        ])
    return JsonResponse({'li1': li1, 'li2': li2})


@csrf_exempt
@login_required(login_url='/adminlogin.html')
@user_passes_test(is_admin, login_url='/adminlogin.html')
def api_deletebook(request, pk):
    """Delete a book by primary key. Used by viewbook.html delete button."""
    if request.method in ('POST', 'DELETE'):
        book = get_object_or_404(models.Book, pk=pk)
        book.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def contactussuccess(request):
    return render(request, 'library/contactussuccess.html')