from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.conf import settings

# ✅ Clean text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ✅ Clean text
def clean_text(text):
    return text.lower().replace(",", " ").replace("\n", " ")


# ✅ ML + Skill Matching (Improved)
def match_resume_ml(resume_text, job_text):

    if not resume_text or not job_text:
        return 0

    # 🔥 STEP 1: Convert skills to sets
    user_set = set(s.strip().lower() for s in resume_text.split(",") if s.strip())
    job_set = set(s.strip().lower() for s in job_text.split(",") if s.strip())

    # 🔥 STEP 2: Find common skills
    common = user_set.intersection(job_set)

    # ❌ If no common skills → no match
    if len(common) == 0:
        return 0

    # 🔥 STEP 3: TF-IDF similarity (ML part)
    resume_text_clean = clean_text(resume_text)
    job_text_clean = clean_text(job_text)

    texts = [resume_text_clean, job_text_clean]

    vectorizer = TfidfVectorizer(
        stop_words='english',
        ngram_range=(1, 2),
        max_features=5000
    )

    vectors = vectorizer.fit_transform(texts)

    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

    # 🔥 STEP 4: Skill-based score
    skill_score = len(common) / len(job_set)

    # 🔥 STEP 5: Final score (Hybrid)
    final_score = (similarity * 0.5 + skill_score * 0.5) * 100

    return round(final_score, 2)


# ✅ Skill Gap Analysis (Improved)
def skill_gap_analysis(user_skills, job_skills):

    user_set = set(skill.strip().lower() for skill in user_skills.split(",") if skill.strip())
    job_set = set(skill.strip().lower() for skill in job_skills.split(",") if skill.strip())

    missing = job_set - user_set

    return sorted(list(missing))

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