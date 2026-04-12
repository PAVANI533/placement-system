from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [

    # Home page (job list)
    path('my-qr/', views.student_qr, name='student_qr'),
    path('', views.custom_login, name='login'),
    path('students/', views.students, name='students'),
    # Registration
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    # Resume uploads
    path('upload-resume/', views.upload_resume, name='upload_resume'),
    path('public-upload/', views.upload_resume_public, name='upload_resume_public'),
    # Job actions
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('company/<int:job_id>/', views.company_page, name='company_page'),
    path('profile/', views.profile, name='profile'),
    # Admin features
    path('add-job/', views.add_job, name='add_job'),
  
    # Password reset flow
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("security-question/", views.security_question, name="security_question"),
    path("reset-password/", views.reset_password, name="reset_password"),
    path('matched-jobs/', views.matched_jobs, name='matched_jobs'),
    # Logout


    path('logout/', views.custom_logout, name='logout'),

    path('resources/', views.resources, name='resources'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('officer/', views.officer_dashboard, name='officer_dashboard'),
    path('redirect-after-login/', views.redirect_after_login, name='redirect_after_login'),
    path('recommended/', views.recommended_jobs, name='recommended_jobs'),
path('add-student/', views.add_student, name='add_student'),
path('update-status/<int:app_id>/', views.update_status, name='update_status'),
path('students/', views.students, name='students'),
path('selected/', views.selected_students, name='selected_students'),
path('applied/', views.applied_jobs, name='applied_jobs'),              # student
path('officer/applied/', views.applied_students, name='applied_students'),  # officer
path('jobs/', views.job_list, name='job_list'),
path('delete-job/<int:job_id>/', views.delete_job, name='delete_job'),
path('edit-job/<int:job_id>/', views.edit_job, name='edit_job'),
path('officer-dashboard/', views.officer_dashboard, name='officer_dashboard'),
path('download-excel/', views.download_excel, name='download_excel'),

]