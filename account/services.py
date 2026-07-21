# account/services.py

from django.core.cache import cache
import random

class OTPService:

    @staticmethod
    def generate():
        return str(random.randint(100000, 999999))

    @staticmethod
    def save(identifier, otp, timeout=300):
        cache.set(f"otp:{identifier}", otp, timeout)

    @staticmethod
    def verify(identifier, otp):
        saved = cache.get(f"otp:{identifier}")
        return saved == otp

    @staticmethod
    def delete(identifier):
        cache.delete(f"otp:{identifier}")