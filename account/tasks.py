from celery import shared_task
from account.utils import send_email


@shared_task
def send_verification_email(email, otp):
    subject = "Verify your email"
    message = f"Your OTP is: {otp}"

    send_email(subject, message, email)