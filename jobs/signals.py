# jobs/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import JobMatch

@receiver(post_save, sender=JobMatch)
def send_jobmatch_email(sender, instance, created, **kwargs):
    if created:
        subject = f"New Job Match: {instance.job.title}"
        message = f"""
Hi {instance.resume.full_name},

You have been matched to the job: {instance.job.title} at {instance.job.company}.
Match Percentage: {instance.percentage}%

Job Location: {instance.job.location}

Please login to your account to apply.
"""
        recipient = [instance.resume.email]

        send_mail(
            subject=subject,
            message=message,
            from_email=None,  # will use DEFAULT_FROM_EMAIL
            recipient_list=recipient,
            fail_silently=False
        )