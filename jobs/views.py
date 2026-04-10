from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import Job, Resume, JobMatch,JobApplication
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth import logout
from .forms import CustomUserRegisterForm
from .utils import match_resume_ml
from .utils import match_resume_ml, skill_gap_analysis







from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login
@login_required
def job_list(request):

    # ❌ Officer should NOT access
    if request.user.is_superuser:
        return redirect('officer_dashboard')

    resume = Resume.objects.filter(user=request.user).first()

    if not resume:
        return redirect('upload_resume')

    jobs = Job.objects.all()

    # ✅ FIX: split skills for template
    for job in jobs:
        job.skills_list = job.required_skills.split(',') if job.required_skills else []
        

    # ✅ OPTIONAL (recommended): applied jobs
    applied_jobs = JobApplication.objects.filter(user=request.user)
    applied_job_ids = [a.job.id for a in applied_jobs]

    # 🔥 ----------- ADD THIS PART ONLY -----------

    total_jobs = jobs.count()
    applied_count = applied_jobs.count()

    not_applied = total_jobs - applied_count

    # you can adjust this logic later
    not_attended = applied_jobs.filter(status="not_attended").count()

    escalations = []

    if not_attended > 0:
        escalations.append(f"You have applied and not attended {not_attended} drives")

    if not_applied > 0:
        escalations.append(f"You have not applied for {not_applied} drives")

    escalations.append(f"You have received {total_jobs} drives")

    # 🔥 ----------- END -----------

    return render(request, "jobs/job_list.html", {
        "jobs": jobs,
        "applied_job_ids": applied_job_ids,

        # 🔥 ADD THIS ONLY
        "escalations": escalations
    })
from .models import Resume


import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
@login_required
def upload_resume(request):
    if request.method == 'POST':
        Resume.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name'),
            email=request.POST.get('email'),
            resume_file=request.FILES.get('resume'),
            skills=request.POST.get('skills')
        )

        # ✅ REDIRECT TO PROFILE UPDATE
        return redirect('update_profile')

    return render(request, 'jobs/upload_resume.html')

# ✅ Extract text from PDF resume
def extract_resume_text(file_path):
    text = ""

    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)

            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted

    except Exception as e:
        print("Error reading PDF:", e)

    return text.lower()


# ✅ ML Matching using TF-IDF
def match_resume_ml(resume_text, job_text):

    if not resume_text or not job_text:
        return 0

    texts = [resume_text, job_text]

    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform(texts)

    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

    return round(similarity * 100, 2)
@csrf_exempt  # disables CSRF checks for public form
def upload_resume_public(request):
    if request.method == 'POST':
        resume_file = request.FILES.get('resume')
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        skills = request.POST.get('skills', '')

        # Validate
        if not resume_file:
            return render(request, 'jobs/upload_resume_public.html', {'error': 'Please upload a file.'})

        # Save to DB
        Resume.objects.create(
            full_name=full_name,
            email=email,
            skills=skills,
            resume_file=resume_file
        )

        return render(request, 'jobs/upload_success.html')

    return render(request, 'jobs/upload_resume_public.html')
from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.is_superuser

from .utils import send_job_notification

@user_passes_test(is_admin)
@login_required
def add_job(request):
    if not request.user.is_superuser:
        return redirect('login')
    
    if request.method == 'POST':
        job = Job.objects.create(   # ✅ FIXED
            title=request.POST.get('title'),
            company=request.POST.get('company'),
            location=request.POST.get('location'),
            description=request.POST.get('description'),
            required_skills=request.POST.get('required_skills'),
            company_url=request.POST.get('company_url'),

            hr_name=request.POST.get('hr_name'),
            package=request.POST.get('package'),
            interview_date=request.POST.get('interview_date')
        )

        send_job_notification(job)   # ✅ now works

        return redirect('officer_dashboard')

    return render(request, 'jobs/add_job.html')

@login_required
def apply_job(request, job_id):
    if request.method == "POST":
        job = get_object_or_404(Job, id=job_id)

        JobApplication.objects.get_or_create(
            user=request.user,
            job=job
        )

        # 🔥 Redirect to company careers page
        return redirect(job.company_url)

    return redirect('job_list')


def company_page(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'jobs/company_page.html', {'job': job})

from .models import UserSecurity

from django.contrib.auth import login, authenticate

from .models import UserProfile

def register(request):
    if request.method == "POST":
        form = CustomUserRegisterForm(request.POST,request.FILES)

        if form.is_valid():
            user = form.save()
            user.set_password(form.cleaned_data.get("password1"))  # 🔥 IMPORTANT
            user.save()

            # 🔥 CREATE PROFILE
            profile, created = UserProfile.objects.get_or_create(user=user)

            # PHOTO
            if request.FILES.get('photo'):
                profile.photo = request.FILES.get('photo')

            # 10th
            profile.tenth_school = request.POST.get('tenth_school')
            profile.tenth_area = request.POST.get('tenth_area')
            profile.tenth_district = request.POST.get('tenth_district')
            profile.tenth_state = request.POST.get('tenth_state')
            profile.tenth_pincode = request.POST.get('tenth_pincode')
            profile.tenth_board = request.POST.get('tenth_board')
            profile.tenth_percentage = request.POST.get('tenth_percentage')
            profile.tenth_year = request.POST.get('tenth_year')

            # INTER
            profile.inter_college = request.POST.get('inter_college')
            profile.inter_area = request.POST.get('inter_area')
            profile.inter_district = request.POST.get('inter_district')
            profile.inter_state = request.POST.get('inter_state')
            profile.inter_pincode = request.POST.get('inter_pincode')
            profile.inter_board = request.POST.get('inter_board')
            profile.inter_stream = request.POST.get('inter_stream')
            profile.inter_percentage = request.POST.get('inter_percentage')
            profile.inter_year = request.POST.get('inter_year')

            # BTECH
            profile.btech_college = request.POST.get('btech_college')
            profile.roll_number = request.POST.get('roll_number')
            profile.department = request.POST.get('department')
            profile.current_year = request.POST.get('current_year')
            profile.passout_year = request.POST.get('passout_year')
            profile.btech_percentage = request.POST.get('btech_percentage')
            profile.backlogs = int(request.POST.get('backlogs') or 0)
            profile.skills = request.POST.get('skills')
            profile.phone = form.cleaned_data.get('phone',"")
            profile.security_question = form.cleaned_data.get('security_question',"")
            profile.security_answer = form.cleaned_data.get('security_answer',"")
            # RESUME
            if request.FILES.get('resume'):
                profile.resume = request.FILES.get('resume')
            try:
                profile.save()
            except Exception as e:
                print(e)
            # LOGIN

            return redirect('login')
        else:
            print(form.errors)


    else:
        form = CustomUserRegisterForm()

    return render(request, "registration/register.html", {"form": form})
    
from django.contrib.auth.models import User
from .models import UserSecurity
from .forms import UsernameForm, SecurityAnswerForm, NewPasswordForm

from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from .models import UserProfile

def security_question(request):
    username = request.session.get("reset_user")

    if not username:
        return redirect("forgot_password")

    user = User.objects.get(username=username)
    profile = user.userprofile

    if request.method == "POST":
        answer = request.POST.get("answer")

        if answer == profile.security_answer:
            return redirect("reset_password")
        else:
            return render(request, "security_question.html", {
                "question": profile.security_question,
                "error": "Wrong answer"
            })

    return render(request, "registration/security_question.html", {
        "question": profile.security_question
    })


def reset_password(request):
    username = request.session.get("reset_user")

    if not username:
        return redirect("forgot_password")

    user = User.objects.get(username=username)

    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            return render(request, "reset_password.html", {
                "error": "Passwords do not match"
            })

        user.set_password(password1)
        user.save()

        return redirect("login")

    return render(request, "registration/reset_password.html")
def forgot_password(request):
    print("METHOD:", request.method)   # debug

    if request.method == "POST":
        username = request.POST.get("username")
        print("USERNAME:", username)   # debug

        from django.contrib.auth.models import User

        try:
            user = User.objects.get(username=username)
            request.session['reset_user'] = user.username
            return redirect("security_question")
        except User.DoesNotExist:
            return render(request, "registration/forgot_password.html", {
                "error": "User not found"
            })

    return render(request, "registration/forgot_password.html")

from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import Job, Resume, JobMatch,JobApplication
from django.views.decorators.csrf import csrf_exempt
from .utils import match_resume_ml
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth import logout
from .forms import CustomUserRegisterForm







from .models import Resume

@login_required


def upload_resume(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        resume_file = request.FILES.get('resume')
        skills = request.POST.get('skills')

        Resume.objects.create(
            user=request.user,
            full_name=full_name,
            email=email,
            resume_file=resume_file,
            skills=skills
        )

        return render(request, 'jobs/job_list.html')  # or redirect somewhere

    return render(request, 'jobs/upload_resume.html')


import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ✅ Extract text from PDF resume
def extract_resume_text(file_path):
    text = ""

    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)

            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted

    except Exception as e:
        print("Error reading PDF:", e)

    return text.lower()


# ✅ ML Matching using TF-IDF
def match_resume_ml(resume_text, job_text):

    if not resume_text or not job_text:
        return 0

    texts = [resume_text, job_text]

    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform(texts)

    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

    return round(similarity * 100, 2)
@csrf_exempt  # disables CSRF checks for public form
def upload_resume_public(request):
    if request.method == 'POST':
        resume_file = request.FILES.get('resume')
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        skills = request.POST.get('skills', '')

        # Validate
        if not resume_file:
            return render(request, 'jobs/upload_resume_public.html', {'error': 'Please upload a file.'})

        # Save to DB
        Resume.objects.create(
            full_name=full_name,
            email=email,
            skills=skills,
            resume_file=resume_file
        )

        return render(request, 'jobs/upload_success.html')

    return render(request, 'jobs/upload_resume_public.html')
from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.is_superuser

@login_required
@login_required
def apply_job(request, job_id):
    if request.method == "POST":
        job = get_object_or_404(Job, id=job_id)

        JobApplication.objects.get_or_create(
            user=request.user,
            job=job
        )

        messages.success(request, "Application submitted successfully!")  # ✅ ADD

        return redirect(job.company_url)

    return redirect('job_list')


def company_page(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'jobs/company_page.html', {'job': job})

from .models import UserSecurity

from django.contrib.auth import login, authenticate

from .models import UserProfile


from django.contrib.auth.models import User
from .models import UserSecurity
from .forms import UsernameForm, SecurityAnswerForm, NewPasswordForm

from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from .models import UserProfile

def security_question(request):
    username = request.session.get("reset_user")

    if not username:
        return redirect("forgot_password")

    user = User.objects.get(username=username)
    profile = user.userprofile

    if request.method == "POST":
        answer = request.POST.get("answer")

        if answer == profile.security_answer:
            return redirect("reset_password")
        else:
            return render(request, "security_question.html", {
                "question": profile.security_question,
                "error": "Wrong answer"
            })

    return render(request, "registration/security_question.html", {
        "question": profile.security_question
    })


def reset_password(request):
    username = request.session.get("reset_user")

    if not username:
        return redirect("forgot_password")

    user = User.objects.get(username=username)

    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            return render(request, "reset_password.html", {
                "error": "Passwords do not match"
            })

        user.set_password(password1)
        user.save()

        return redirect("login")

    return render(request, "registration/reset_password.html")
def forgot_password(request):
    print("METHOD:", request.method)   # debug

    if request.method == "POST":
        username = request.POST.get("username")
        print("USERNAME:", username)   # debug

        from django.contrib.auth.models import User

        try:
            user = User.objects.get(username=username)
            request.session['reset_user'] = user.username
            return redirect("security_question")
        except User.DoesNotExist:
            return render(request, "registration/forgot_password.html", {
                "error": "User not found"
            })

    return render(request, "registration/forgot_password.html")

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Resume, Job, JobApplication

@login_required
def matched_jobs(request):

    resume = Resume.objects.filter(user=request.user).first()

    if not resume:
        return redirect('upload_resume')

    jobs = Job.objects.all()
    matched = []

    for job in jobs:
        score = match_resume_ml(resume.skills, job.required_skills)

        if score >= 20:
            missing_skills = skill_gap_analysis(resume.skills, job.required_skills)

            matched.append({
                "job": job,
                "missing": missing_skills
            })

    applied_jobs = JobApplication.objects.filter(user=request.user).values_list('job_id', flat=True)

    return render(request, "jobs/matched_jobs.html", {
        "jobs": matched,
        "applied_jobs": applied_jobs
    })
def resources(request):
    return render(request, "jobs/resources.html")


from django.contrib.auth.decorators import login_required
from .models import JobApplication


@login_required
def applied_students(request):
    company = request.GET.get('company')
    department = request.GET.get('department')

    jobs = Job.objects.all()
    applications = JobApplication.objects.all()

    if company:
        job = Job.objects.filter(company=company).first()
        if job:
            applications = applications.filter(job=job)

    if department:
        applications = applications.filter(user__userprofile__department=department)

    return render(request, 'jobs/applied_students.html', {
        'applications': applications,
        'jobs': jobs
    })
from .models import Resume   # ✅ import this

@login_required
def profile(request):
    profile = request.user.userprofile

    return render(request, 'jobs/profile.html', {
        'profile': profile
    })

from django.contrib.auth.decorators import login_required
from .forms import ProfileForm


from django.contrib.auth.decorators import user_passes_test
from .models import UserProfile, Job, JobApplication

def is_officer(user):
    return user.userprofile.role == 'officer'

@login_required
def update_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    edit_section = request.GET.get('edit')   # ✅ VERY IMPORTANT

    if request.method == "POST":

        # detect which section is editing
        edit_section = request.GET.get('edit')

        if edit_section == "photo":
            if request.FILES.get('photo'):
                profile.photo = request.FILES.get('photo')

        elif edit_section == "tenth":
            profile.tenth_school = request.POST.get('tenth_school')
            profile.tenth_area = request.POST.get('tenth_area')
            profile.tenth_district = request.POST.get('tenth_district')
            profile.tenth_state = request.POST.get('tenth_state')
            profile.tenth_pincode = request.POST.get('tenth_pincode')
            profile.tenth_board = request.POST.get('tenth_board')
            profile.tenth_percentage = request.POST.get('tenth_percentage')
            profile.tenth_year = request.POST.get('tenth_year')

        elif edit_section == "inter":
            profile.inter_college = request.POST.get('inter_college')
            profile.inter_area = request.POST.get('inter_area')
            profile.inter_district = request.POST.get('inter_district')
            profile.inter_state = request.POST.get('inter_state')
            profile.inter_pincode = request.POST.get('inter_pincode')
            profile.inter_board = request.POST.get('inter_board')
            profile.inter_stream = request.POST.get('inter_stream')
            profile.inter_percentage = request.POST.get('inter_percentage')
            profile.inter_year = request.POST.get('inter_year')

        elif edit_section == "btech":
            profile.btech_college = request.POST.get('btech_college')
            profile.roll_number = request.POST.get('roll_number')
            profile.department = request.POST.get('department')
            profile.current_year = request.POST.get('current_year')
            profile.btech_percentage = request.POST.get('btech_percentage')
            profile.passout_year = request.POST.get('passout_year')
            profile.backlogs = request.POST.get('backlogs') or 0
            profile.skills = request.POST.get('skills')

        elif edit_section == "resume":
            if request.FILES.get('resume'):
                profile.resume = request.FILES.get('resume')

        profile.save()

        return redirect('update_profile')   # back to view mode

    return render(request, 'jobs/update_profile.html', {
        'profile': profile,
        'edit_section': edit_section   # ✅ PASS THIS
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Job, JobApplication, UserProfile

from django.utils.timezone import now
from datetime import timedelta


from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def officer_dashboard(request):
    if not request.user.is_superuser:
        return redirect('login')

    view_type = request.GET.get('view')
    dept = request.GET.get('department')
    job_id = request.GET.get('job')

    students = UserProfile.objects.filter(user__is_superuser=False)
    jobs = Job.objects.all()

    # ⭐ DASHBOARD STATS
    total_students = students.count()
    total_jobs = jobs.count()
    total_placed = JobApplication.objects.filter(status='placed').count()

    placement_percentage = 0
    if total_students > 0:
        placement_percentage = (total_placed / total_students) * 100

    data = []
    today = date.today()

    for job in jobs:
        
    # ✅ FILTER BY CLICKED JOB
        if job_id and str(job.id) != job_id:
            continue
        # ✅ APPLIED
        applied = JobApplication.objects.filter(job=job).select_related('user')

        # ✅ FILTER BY DEPARTMENT
        if dept:
            applied = applied.filter(user__userprofile__department=dept)

        # ✅ SELECTED
        selected = applied.filter(status='selected')

        # ✅ NOT APPLIED (ONLY FOR THIS JOB)
        applied_users = JobApplication.objects.filter(job=job).values_list('user', flat=True)

        not_applied = students.exclude(user__in=applied_users)

        if dept:
            not_applied = not_applied.filter(department=dept)

        # ✅ STATUS
        if job.interview_date:
            if job.interview_date < today:
                job_status = "Completed"
            elif job.interview_date == today:
                job_status = "Ongoing"
            else:
                job_status = "Upcoming"
        else:
            job_status = "Not Scheduled"

        # ✅ APPEND DATA (INSIDE LOOP)
        data.append({
            'job': job,
            'applied': applied,
            'selected': selected,
            'not_applied': not_applied,
            'status': job_status
        })

    return render(request, 'jobs/officer_dashboard.html', {
        'data': data,
        'view_type': view_type,
        'selected_job': job_id,
        'total_students': total_students,
        'total_jobs': total_jobs,
        'total_placed': total_placed,
        'placement_percentage': placement_percentage
    })
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from django.shortcuts import redirect
from django.shortcuts import redirect

def redirect_after_login(request):
    if request.user.is_superuser:
        return redirect('officer_dashboard')

    # student flow
    profile = request.user.userprofile

    if not profile.resume:
        return redirect('upload_resume')

    if not profile.department:
        return redirect('update_profile')

    return redirect('job_list')
    
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect


from django.contrib.auth.decorators import login_required



from django.contrib.auth.decorators import login_required
from .models import Job, UserProfile, JobApplication

from django.contrib.auth.decorators import login_required
from .models import Job, UserProfile, JobApplication

@login_required
def recommended_jobs(request):
    profile = request.user.userprofile

    # ✅ Get all jobs
    jobs = Job.objects.all()

    # ✅ If student has skills → filter jobs
    if profile.skills:
        user_skills = [s.strip().lower() for s in profile.skills.split(',') if s.strip()]

        filtered_jobs = []

        for job in jobs:
            if job.required_skills:
                job_skills = job.required_skills.lower()

                # ✅ match ANY skill
                if any(skill in job_skills for skill in user_skills):
                    filtered_jobs.append(job)

        jobs = filtered_jobs

    # ✅ ADD skills_list for template (IMPORTANT FIX)
    for job in jobs:
        job.skills_list = job.required_skills.split(',') if job.required_skills else []

    return render(request, 'jobs/recommended_jobs.html', {
        'jobs': jobs
    })


@login_required
def applied_jobs(request):

    # ✅ get applications of logged-in user
    applications = JobApplication.objects.filter(user=request.user).select_related('job')

    # ✅ add skills_list
    for app in applications:
        if app.job.required_skills:
            app.job.skills_list = app.job.required_skills.split(',')
        else:
            app.job.skills_list = []

    return render(request, 'jobs/applied_jobs.html', {
        'applications': applications
    })


from django.contrib.auth.models import User

@login_required
def add_student(request):
    if not request.user.is_superuser:
        return redirect('login')

    if request.method == 'POST':
        user = User.objects.create_user(
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        UserProfile.objects.create(
            user=user,
            department=request.POST.get('department'),
            percentage=request.POST.get('percentage'),
            skills=request.POST.get('skills')
        )

        return redirect('officer_dashboard')

    return render(request, 'jobs/add_student.html')

@login_required
def update_status(request, app_id):

    if not request.user.is_superuser:
        return redirect('login')

    app = JobApplication.objects.get(id=app_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        job_id = request.POST.get('job')
        view_type = request.POST.get('view')

        if status:
            app.status = status
            app.save()

        # ✅ REDIRECT BACK TO SAME PAGE
        return redirect(f'/officer-dashboard/?job={job_id}&view={view_type}')

    return redirect('officer_dashboard')


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

@login_required
def students(request):
    if not request.user.is_superuser:
        return redirect('login')

    students = UserProfile.objects.filter(user__is_superuser=False)

    dept = request.GET.get('department')

    if dept:
        students = students.filter(department=dept)

    return render(request, 'jobs/students.html', {'students': students})


@login_required
def selected_students(request):
    company = request.GET.get('company')
    department = request.GET.get('department')

    jobs = Job.objects.all()
    selected = JobApplication.objects.filter(status='selected')

    if company:
        job = Job.objects.filter(company=company).first()
        if job:
            selected = selected.filter(job=job)

    if department:
        selected = selected.filter(user__userprofile__department=department)

    return render(request, 'jobs/selected_students.html', {
        'selected': selected,
        'jobs': jobs
    })

from django.contrib.auth import logout

def custom_logout(request):
    logout(request)
    return redirect('login')

@login_required
def student_dashboard(request):
    profile = UserProfile.objects.get(user=request.user)

    if not profile.resume:
        return redirect('update_profile')   # only if missing

    return render(request, 'jobs/student_dashboard.html')

from django.shortcuts import redirect, get_object_or_404



from django.contrib.auth import authenticate, login


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    edit_section = request.GET.get('edit')

    return render(request, 'profile.html', {
        'profile': profile,
        'edit_section': edit_section
    })

from django.core.mail import send_mail
from django.contrib.auth.models import User

def send_job_notification(job):

    students = User.objects.filter(is_superuser=False)

    email_list = [s.email for s in students if s.email]

    subject = f"New Job Posted: {job.title}"

    message = f"""
    A new job has been posted!

    Company: {job.company}
    Role: {job.title}
    Location: {job.location}
    Skills: {job.required_skills}

    Apply now in the portal.
    """

    send_mail(
        subject,
        message,
        'your_email@gmail.com',
        email_list,
        fail_silently=False,
    )

def custom_login(request):
    if request.method == "POST":
        role = request.POST.get("role")
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        # ❌ INVALID CREDENTIALS
        if user is None:
            return render(request, "registration/login.html", {
                "error": "Invalid username or password"
            })

        # 👨‍💼 OFFICER LOGIN
        if role == "officer":
            if user.is_superuser:
                login(request, user)
                return redirect('officer_dashboard')
            else:
                return render(request, "registration/login.html", {
                    "error": "You are not an officer"
                })

        # 👨‍🎓 STUDENT LOGIN
        elif role == "student":
            if not user.is_superuser:
                login(request, user)

                profile = user.userprofile

                if not Resume.objects.filter(user=user).exists():
                    return redirect('upload_resume')

                if not profile.department:
                    return redirect('update_profile')

                return redirect('job_list')
            else:
                return render(request, "registration/login.html", {
                    "error": "You are not a student"
                })

    return render(request, "registration/login.html")

from django.shortcuts import get_object_or_404

@login_required
def delete_job(request, job_id):

    # only officer can delete
    if not request.user.is_superuser:
        return redirect('job_list')

    job = get_object_or_404(Job, id=job_id)
    job.delete()

    return redirect('officer_dashboard')
@login_required
def edit_job(request, job_id):
    if not request.user.is_superuser:
        return redirect('login')

    job = Job.objects.get(id=job_id)

    if request.method == "POST":
        job.title = request.POST.get('title')
        job.company = request.POST.get('company')
        job.location = request.POST.get('location')
        job.package = request.POST.get('package')
        job.hr_name = request.POST.get('hr_name')
        job.interview_date = request.POST.get('interview_date')
        job.required_skills = request.POST.get('skills')
        job.description = request.POST.get('description')

        job.save()
        return redirect('officer_dashboard')

    return render(request, 'jobs/edit_job.html', {'job': job})


import openpyxl
from django.http import HttpResponse

@login_required
def download_excel(request):

    if not request.user.is_superuser:
        return redirect('login')

    view_type = request.GET.get('view')
    job_id = request.GET.get('job')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Students"

    # HEADERS
    ws.append([
        "Name", "Roll Number", "Department",
        "Email", "CGPA", "Backlogs", "Year"
    ])

    if job_id:
        job = Job.objects.get(id=job_id)

        if view_type == "applied":
            data = JobApplication.objects.filter(job=job)

        elif view_type == "selected":
            data = JobApplication.objects.filter(job=job, status="selected")

        elif view_type == "not_applied":
            applied_users = JobApplication.objects.filter(job=job).values_list('user', flat=True)
            data = UserProfile.objects.exclude(user__in=applied_users)

        else:
            data = []

        for obj in data:

            if view_type == "not_applied":
                user = obj.user
                profile = obj
            else:
                user = obj.user
                profile = user.userprofile

            ws.append([
                user.username,
                profile.roll_number,
                profile.department,
                user.email,
                profile.cgpa,
                profile.backlogs,
                profile.current_year
            ])

    # RESPONSE
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{view_type}_students.xlsx"'

    wb.save(response)
    return response

import qrcode
from io import BytesIO
import base64

@login_required
def student_qr(request):
    user = request.user
    profile = user.userprofile

    # what data you want inside QR
    data = f"Name: {user.username}, Roll: {profile.roll_number}"

    qr = qrcode.make(data)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'jobs/student_qr.html', {
    'profile': profile,
    'qr_code': img_str   # ✅ IMPORTANT
})