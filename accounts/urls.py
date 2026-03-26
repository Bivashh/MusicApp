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
    # Teacher
    path("teacher/assessments/", views.teacher_assessments, name="teacher_assessments"),
    path("teacher/assessments/create/", views.teacher_create_assessment, name="teacher_create_assessment"),
    path("teacher/assessments/<int:assessment_id>/submissions/", views.teacher_submissions, name="teacher_submissions"),
    path("teacher/submission/<int:submission_id>/grade/", views.teacher_grade_submission, name="teacher_grade_submission"),
    path("teacher/dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
    path("teacher/profile/", views.teacher_profile, name="teacher_profile"),
    #path("teacher/classes/", views.teacher_classes, name="teacher_classes"),
    # Student
    path("student/assessments/", views.student_assessments, name="student_assessments"),
    path("student/assessments/<int:assessment_id>/submit/", views.student_submit_assessment, name="student_submit_assessment"),
    path("student/results/", views.student_results, name="student_results"),
    path("logout/", views.logout_view, name="logout"),

    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("resend-otp/", views.resend_otp, name="resend_otp"),
]