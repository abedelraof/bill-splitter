import os
import secrets

SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# DATA_DIR is set on Fly.io to the persistent volume mount point (/data).
# Locally it defaults to the project root so behaviour is unchanged.
DATA_DIR = os.getenv("DATA_DIR", ".")
DATABASE_URL = f"sqlite:///{DATA_DIR}/billsplitter.db"
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
