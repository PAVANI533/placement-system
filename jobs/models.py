from django.db import models
from django.contrib.auth.models import User


class Job(models.Model):
    title = models.CharField(max_length=200,null=True,blank=True)
    company = models.CharField(max_length=200,null=True,blank=True)

    hr_name = models.CharField(max_length=200, null=True, blank=True)

    package = models.CharField(max_length=200, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)

    interview_date = models.DateField(null=True, blank=True)

    required_skills = models.TextField()
    description = models.TextField()
    eligible_departments = models.CharField(max_length=200,null=True,blank=True)
    min_percentage = models.FloatField(null=True, blank=True) 
    company_url = models.URLField(null=True, blank=True)
    def __str__(self):
        return self.title


from django.db import models

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    resume_file = models.FileField(upload_to='resumes/')
    skills = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    print(resume_file)
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
class JobMatch(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    percentage = models.IntegerField()

    candidate_name = models.CharField(max_length=150, null=True, blank=True)
    candidate_email = models.EmailField(null=True, blank=True)
    candidate_id = models.IntegerField(null=True, blank=True)
    company_name = models.CharField(max_length=200, null=True, blank=True)
    job_location = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.candidate_name} - {self.job.title} ({self.percentage}%)"
    
class JobApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.job.title}"
    
SECURITY_QUESTIONS = [
    ("school", "What is your first school name?"),
    ("pet", "What is your first pet name?"),
    ("city", "In which city were you born?"),
]
from django.contrib.auth.models import User
from django.db import models

from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10,default="student")
    # 📸 Photo
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)

    # 🏫 10th
    tenth_school = models.CharField(max_length=200, null=True, blank=True)
    tenth_area = models.CharField(max_length=100, null=True, blank=True)
    tenth_district = models.CharField(max_length=100, null=True, blank=True)
    tenth_state = models.CharField(max_length=100, null=True, blank=True)
    tenth_pincode = models.CharField(max_length=10, null=True, blank=True)
    tenth_board = models.CharField(max_length=50, null=True, blank=True)
    tenth_percentage = models.FloatField(null=True, blank=True)
    tenth_year = models.IntegerField(null=True, blank=True)

    # 🏫 Inter
    inter_college = models.CharField(max_length=200, null=True, blank=True)
    inter_area = models.CharField(max_length=100, null=True, blank=True)
    inter_district = models.CharField(max_length=100, null=True, blank=True)
    inter_state = models.CharField(max_length=100, null=True, blank=True)
    inter_pincode = models.CharField(max_length=10, null=True, blank=True)
    inter_board = models.CharField(max_length=50, null=True, blank=True)
    inter_stream = models.CharField(max_length=50, null=True, blank=True)
    inter_percentage = models.FloatField(null=True, blank=True)
    inter_year = models.IntegerField(null=True, blank=True)

    # 🎓 B.Tech
    btech_college = models.CharField(max_length=200, null=True, blank=True)
    roll_number = models.CharField(max_length=50, null=True, blank=True)
    department = models.CharField(max_length=50, null=True, blank=True)
    skills = models.TextField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    btech_percentage = models.FloatField(null=True, blank=True)
    passout_year = models.IntegerField(null=True, blank=True)
    current_year = models.IntegerField(null=True, blank=True)
    backlogs = models.IntegerField(default=0)
    cgpa = models.FloatField(null=True, blank=True)
    
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

from django.contrib.auth.hashers import make_password, check_password

class UserSecurity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    security_question = models.CharField(max_length=255)
    security_answer = models.CharField(max_length=255)

    def set_answer(self, raw_answer):
        self.security_answer = make_password(raw_answer)

    def check_answer(self, raw_answer):
        return check_password(raw_answer, self.security_answer)
    
@receiver(post_save, sender=User)
def create_user_security(sender, instance, created, **kwargs):
    if created:
        UserSecurity.objects.create(user=instance)


from django.contrib.auth.models import User
from django.db import models

class JobApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    eligible_departments = models.CharField(max_length=200)  # ex: "CSE,IT"
    min_percentage = models.FloatField(null=True, blank=True)
    # ✅ ADD THIS HERE
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
        ('not_attended', 'Not Attended'),   # ✅ ADD THIS
]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
