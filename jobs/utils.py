from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.conf import settings

# ✅ Clean text
def clean_text(text):
    return text.lower().replace(",", " ").replace("\n", " ")


# ✅ ML Matching (TF-IDF + Cosine Similarity)
def match_resume_ml(resume_text, job_text):

    if not resume_text or not job_text:
        return 0

    resume_text = clean_text(resume_text)
    job_text = clean_text(job_text)

    texts = [resume_text, job_text]

    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1,2))
    vectors = vectorizer.fit_transform(texts)

    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

    return round(similarity * 100, 2)

def skill_gap_analysis(user_skills, job_skills):
    user_set = set(skill.strip().lower() for skill in user_skills.split(","))
    job_set = set(skill.strip().lower() for skill in job_skills.split(","))

    missing = job_set - user_set

    return list(missing)

from django.core.mail import send_mail
from django.contrib.auth.models import User

from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings

from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings



def send_job_notification(job):

    print("🔥 FUNCTION STARTED")

    students = User.objects.filter(is_superuser=False)

    print("👤 All Users:", list(User.objects.values_list('username', 'email')))

    email_list = list(
        students.exclude(email__isnull=True)
        .exclude(email__exact="")
        .values_list('email', flat=True)
    )

    print("📧 Emails:", email_list)
    print("📤 FROM:", settings.DEFAULT_FROM_EMAIL)
    print("📡 BACKEND:", settings.EMAIL_BACKEND)

    if not email_list:
        print("❌ No emails found")
        return

    try:
        result = send_mail(
    f"New Job Opportunity at {job.company}",
    f"""
Dear Student,

We are pleased to inform you that a new job opportunity has been posted on the Placement Portal.

📌 Company: {job.company}
💼 Package: {job.package}
🛠 Required Skills: {job.required_skills}

We encourage you to log in to the Placement System and apply as soon as possible.

🔗 Visit: Placement Portal

Best regards,  
Placement Cell  
""",
    settings.DEFAULT_FROM_EMAIL,
    email_list,
    fail_silently=False,
)
        print("✅ Send result:", result)

    except Exception as e:
        print("❌ Email Error:", e)