# pages/two_factor_auth/two_factor_utils.py
import pyotp

def generate_2fa_code(secret_key: str):
    """Генерирует 6-значный 2FA код на основе секретного ключа"""
    try:
        totp = pyotp.TOTP(secret_key)
        return totp.now()
    except Exception as e:
        print(f"❌ Ошибка генерации 2FA кода: {e}")
        return None