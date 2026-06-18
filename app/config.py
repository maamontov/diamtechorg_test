import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/testdb")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
WEBHOOK_SECRET_KEY = os.getenv("WEBHOOK_SECRET_KEY", "gfdmhghif38yrf9ew0jkf32")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24
