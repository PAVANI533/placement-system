try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    ML_AVAILABLE = True
except:
    ML_AVAILABLE = False


def clean_text(text):
    return text.lower().replace(",", " ").replace("\n", " ")


def match_resume_ml(resume_text, job_text):

    if not resume_text or not job_text:
        return 0

    resume_text = clean_text(resume_text)
    job_text = clean_text(job_text)

    if ML_AVAILABLE:
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1,2))
        vectors = vectorizer.fit_transform([resume_text, job_text])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        return round(similarity * 100, 2)
    else:
        common = set(resume_text.split()) & set(job_text.split())
        score = len(common) / max(len(job_text.split()), 1)
def skill_gap_analysis(resume_text, job_description):
    resume_words = set(clean_text(resume_text).split())
    job_words = set(clean_text(job_description).split())

    missing_skills = job_words - resume_words

    return list(missing_skills)[:10]  # show top 10 missing skills
def send_job_notification(user, job):
    print(f"Notification sent to {user} for job {job}")