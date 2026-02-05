import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Temel yapılandırma sınıfı"""
    
    # Flask temel ayarları
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Veritabanı
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///cmms.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Oturum yönetimi
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Dosya yükleme
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xls', 'xlsx'}
    
    # Öngörücü bakım parametreleri
    PREDICTION_MODEL_PATH = 'models/predictive_maintenance.pkl'
    PREDICTION_THRESHOLD = 0.7
    
    # KPI hesaplama periyodu (saniye)
    KPI_CALCULATION_INTERVAL = 3600  # Her saat
    
    # Bildirim ayarları
    ENABLE_EMAIL_NOTIFICATIONS = False
    ENABLE_SMS_NOTIFICATIONS = False
    
    # API ayarları
    API_VERSION = 'v1'
    API_RATE_LIMIT = '100/hour'
    
    # Sayfalama
    ITEMS_PER_PAGE = 50
    
    # Dil ve zaman dilimi
    DEFAULT_LANGUAGE = 'tr'
    TIMEZONE = 'Europe/Istanbul'
    
    # Güvenlik
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_SPECIAL = True
    PASSWORD_REQUIRE_NUMBERS = True
    LOGIN_MAX_ATTEMPTS = 5
    LOGIN_BLOCK_DURATION = 15  # dakika


class DevelopmentConfig(Config):
    """Geliştirme ortamı yapılandırması"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Üretim ortamı yapılandırması"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Test ortamı yapılandırması"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_cmms.db'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
