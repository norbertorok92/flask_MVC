class Config:
  SECRET_KEY = '72109f9aed8e0f7b633091e2adbba912'
  CORS_HEADERS = 'Content-Type'
  SQLALCHEMY_DATABASE_URI = 'sqlite:///mpa_app.db'
  MAIL_SERVER = 'smtp.googlemail.com'
  MAIL_PORT = 587
  MAIL_USE_TLS = True