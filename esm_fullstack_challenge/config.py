from starlette.config import Config

config = Config()
ENVIRONMENT = config('ENVIRONMENT', default='development')
PORT = config('PORT', cast=int, default=8000)
CORS_ORIGINS = config('CORS_ORIGINS', default='http://localhost:5173')
DB_FILE = config('DB_FILE', default='data.db')

SECRET_KEY = config('SECRET_KEY', default='dev-secret-key-change-in-production')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = config('ACCESS_TOKEN_EXPIRE_MINUTES', cast=int, default=60)
