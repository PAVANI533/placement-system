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
    if not settings.EMAIL_HOST_USER:
        print("Email not configured")
        return

    students = User.objects.filter(is_superuser=False)

    subject = f"New Job Opportunity: {job.company}"

    message = f"""
New Job Posted!

Company: {job.company}
Package: {job.package}
Skills Required: {job.required_skills}

Apply now in Placement System.
"""

    for user in students:
        if user.email:
            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print("Email failed for:", user.email, e)