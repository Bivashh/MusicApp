from django.urls import path
from . import views

urlpatterns=[
    path("", views.home, name="home"),
    path("panel/login/", views.admin_login, name="admin_login"),
    path("panel/logout/", views.admin_logout, name="admin_logout"),
    path("panel/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("panel/students/", views.admin_students, name="admin_students"),
    path("panel/teachers/", views.admin_teachers, name="admin_teachers"),
    path("panel/payments/", views.admin_payments, name="admin_payments"),

    path("panel/student/delete/<int:student_id>/", views.admin_delete_student, name="admin_delete_student"),
    path("panel/teacher/delete/<int:teacher_id>/", views.admin_delete_teacher, name="admin_delete_teacher"),

    path('register/student/', views.student_register, name='student_register'),
    path('register/teacher/', views.teacher_register, name='teacher_register'),
    path('login/', views.loginPage, name='login'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher/create-class/', views.create_class, name='create_class'),
    path("student/profile/", views.student_profile, name="student_profile"),
    path("student/payments/", views.student_payment, name="student_payment"),
    path("student/payments/new/", views.student_payment_new, name="student_payment_new"),
    path("khalti/initiate/<int:payment_id>/", views.khalti_initiate, name="khalti_initiate"),
    path("khalti/return/", views.khalti_return, name="khalti_return"),
]