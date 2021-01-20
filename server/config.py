
import smtplib, ssl

D_NAME = 'edu.universityofmars.com'

class Config():
    DEBUG                   = False
    TESTING                 = False

    DB_NAME                 = 'production-db'
    DB_USER                 = 'production-user'
    DB_PASS                 = 'production-pass'
    DB_HOST                 = 'localhost'

    DB_ADMIN_USER           = 'db-admin-user'
    DB_ADMIN_PASS           = 'db-admin-password'

    SECRET_KEY              = 'tdyfwhwegfgdfgjhzgj'
    SESSION_COOKIE_SECURE   = True

    # Email setup
    EMAIL_HOST              = f'{D_NAME}.com'
    EMAIL_PASS              = 'Thepassword@root247'

    EMAIL_SMTP_SECURITY     = smtplib.SMTP_SSL

    EMAIL_USER         = f'info@{D_NAME}.com'
    EMAIL_NOREPLY_USER = f'noreply@{D_NAME}.com'


class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG                   = True
    SESSION_COOKIE_SECURE   = False

    # Database setup
    DB_NAME                 = D_NAME
    DB_USER                 = 'busybox'
    DB_PASS                 = 'grandMix@2020'

    # Email setup
    EMAIL_HOST              = 'smtp.mailtrap.io'
    EMAIL_PASS              = 'c789c7676d38e5'

    EMAIL_SMTP_SECURITY     = smtplib.SMTP

    EMAIL_USER              = '8bcf97fe492eaf'
    EMAIL_NOREPLY_USER      = f'noreply@{D_NAME}.com'

class TestingConfig(Config):
    TESTING                 = True
    SESSION_COOKIE_SECURE   = False