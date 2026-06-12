from django.contrib import admin
from django.urls import path, include
from library import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # Health check (for AWS ALB / ECS / EC2 monitoring)
    path('health/', views.health, name='health'),

    # Django auth URLs (password reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # ── Public pages ──────────────────────────────────────────────────────────
    path('', views.home_view, name='home'),
    path('adminclick.html', views.adminclick_view, name='adminclick'),
    path('studentclick.html', views.studentclick_view, name='studentclick'),
    path('aboutus.html', views.aboutus_view, name='aboutus'),
    path('contactus.html', views.contactus_view, name='contactus'),
    path('contactussuccess.html', views.contactussuccess, name='contactussuccess'),

    # ── Authentication ────────────────────────────────────────────────────────
    path('adminlogin.html', views.adminlogin_view, name='adminlogin'),
    path('studentlogin.html', views.studentlogin_view, name='studentlogin'),
    path('studentsignup.html', views.studentsignup_view, name='studentsignup'),
    path('adminsignup.html', views.adminsignup_view, name='adminsignup'),

    # FIX: LogoutView in Django 5.x only accepts POST; next_page sends user to home
    path('logout/', LogoutView.as_view(), name='logout'),

    # After-login dispatchers
    path('afterlogin.html', views.afterlogin_view, name='afterlogin'),
    path('studentafterlogin.html', views.studentafterlogin_view, name='studentafterlogin'),
    path('adminafterlogin.html', views.adminafterlogin_view, name='adminafterlogin'),

    # ── Admin-only pages ──────────────────────────────────────────────────────
    path('addbook.html', views.addbook_view, name='addbook'),
    path('bookadded.html', views.bookadded_view, name='bookadded'),
    path('viewbook.html', views.viewbook_view, name='viewbook'),
    path('api/issuebook/', views.issuebook_view, name='issuebook'),
    path('bookissued.html', views.bookissued_view, name='bookissued'),
    path('viewissuedbook.html', views.viewissuedbook_view, name='viewissuedbook'),
    path('viewstudent.html', views.viewstudent_view, name='viewstudent'),

    # ── Student pages ─────────────────────────────────────────────────────────
    path('viewissuedbookbystudent/', views.viewissuedbookbystudent, name='viewissuedbookbystudent'),
    path('returnbook/<int:id>/', views.return_book, name='returnbook'),

    # ── JSON API endpoints (consumed by JS fetch() in HTML templates) ─────────
    path('api/books/', views.api_books, name='api_books'),
    path('api/students/', views.api_students, name='api_students'),
    path('api/issuedbooks/', views.api_issuedbooks, name='api_issuedbooks'),
    path('api/myissuedbooks/', views.api_myissuedbooks, name='api_myissuedbooks'),
    path('api/deletebook/<int:pk>/', views.api_deletebook, name='api_deletebook'),
]
