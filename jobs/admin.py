from django.contrib import admin
from .models import Job, Resume, JobMatch


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location')
    search_fields = ('title', 'company')


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'skills', 'uploaded_at')
    search_fields = ('full_name', 'email', 'skills')
    list_filter = ('uploaded_at',)


@admin.register(JobMatch)
class JobMatchAdmin(admin.ModelAdmin):
    list_display = ('candidate_name', 'job', 'percentage', 'company_name', 'job_location')

    def candidate_name(self, obj):
        return obj.resume.user.get_full_name() or obj.resume.user.username
    candidate_name.short_description = 'Candidate Name'