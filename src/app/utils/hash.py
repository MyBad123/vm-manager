import hashlib
import hmac
import os


class Hash:
    """class for work with hash for password"""

    @staticmethod
    def hash_password_with_key(str_password):
        """make hash for password"""

        secret_key = os.environ.get('SECRET_KEY')

        hmac_hash = hmac.new(secret_key.encode(), str_password.encode(), hashlib.sha256)
        return hmac_hash.hexdigest()
