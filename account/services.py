from django.core.cache import cache
import secrets


class OTPService:
    PREFIX = "otp"
    OTP_LENGTH = 6
    OTP_TIMEOUT = 300  # 5 minutes

    @classmethod
    def _key(cls, identifier: str) -> str:
        return f"{cls.PREFIX}:{identifier}"

    @staticmethod
    def generate() -> str:
        return str(secrets.randbelow(900000) + 100000)

    @classmethod
    def save(cls, identifier: str, otp: str, timeout: int = None) -> None:
        cache.set(
            cls._key(identifier),
            otp,
            timeout or cls.OTP_TIMEOUT,
        )

    @classmethod
    def verify(cls, identifier: str, otp: str) -> bool:
        if not otp:
            return False

        saved = cache.get(cls._key(identifier))

        if saved is None:
            return False

        if str(saved) != str(otp):
            return False

        # One-time use
        cache.delete(cls._key(identifier))
        return True

    @classmethod
    def delete(cls, identifier: str) -> None:
        cache.delete(cls._key(identifier))