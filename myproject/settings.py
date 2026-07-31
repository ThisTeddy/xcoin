from pathlib import Path
from decouple import config
import cloudinary
# ==================================================

# PATHS

# ==================================================



BASE_DIR = Path(__file__).resolve().parent.parent


# ==================================================
# CLOUDINARY
# ==================================================

CLOUDINARY_CLOUD_NAME = config(
    "CLOUDINARY_CLOUD_NAME",
    default="",
)

CLOUDINARY_API_KEY = config(
    "CLOUDINARY_API_KEY",
    default="",
)

CLOUDINARY_API_SECRET = config(
    "CLOUDINARY_API_SECRET",
    default="",
)

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True,
)
# ==================================================

# SECURITY

# ==================================================

SECRET_KEY = config(
"SECRET_KEY",
default="django-insecure-change-this-in-production"
)

DEBUG = config(
"DEBUG",
default=True,
cast=bool,
)

ALLOWED_HOSTS = config(
"ALLOWED_HOSTS",
default="*",
cast=lambda value: [
host.strip()
for host in value.split(",")
if host.strip()
],
)

# ==================================================

# APPLICATIONS

# ==================================================

INSTALLED_APPS = [

# XCoin
"xcoin",

# Cloudinary
"cloudinary",

# Django
"django.contrib.humanize",
"django.contrib.admin",
"django.contrib.auth",
"django.contrib.contenttypes",
"django.contrib.sessions",
"django.contrib.messages",
"django.contrib.staticfiles",


]


# ==================================================

# MIDDLEWARE

# ==================================================

MIDDLEWARE = [


"django.middleware.security.SecurityMiddleware",

# Static files
"whitenoise.middleware.WhiteNoiseMiddleware",

"django.contrib.sessions.middleware.SessionMiddleware",

"django.middleware.common.CommonMiddleware",

"django.middleware.csrf.CsrfViewMiddleware",

"django.contrib.auth.middleware.AuthenticationMiddleware",

"django.contrib.messages.middleware.MessageMiddleware",

"django.middleware.clickjacking.XFrameOptionsMiddleware",


]

# ==================================================

# URL CONFIGURATION

# ==================================================

ROOT_URLCONF = "myproject.urls"

# ==================================================

# TEMPLATES

# ==================================================

TEMPLATES = [


{

    "BACKEND":
        "django.template.backends.django.DjangoTemplates",

    "DIRS": [
        BASE_DIR / "templates",
    ],

    "APP_DIRS": True,

    "OPTIONS": {

        "context_processors": [

            "django.template.context_processors.request",

            "django.contrib.auth.context_processors.auth",

            "django.contrib.messages.context_processors.messages",

            "xcoin.context_processors.notifications",

        ],

    },

},


]

# ==================================================

# WSGI

# ==================================================

WSGI_APPLICATION = "myproject.wsgi.application"

# ==================================================

# DATABASE

# ==================================================

DATABASES = {


"default": {

    "ENGINE":
        "django.db.backends.sqlite3",

    "NAME":
        BASE_DIR / "db.sqlite3",

}


}

# ==================================================

# PASSWORD VALIDATION

# ==================================================

AUTH_PASSWORD_VALIDATORS = [


{
    "NAME":
        "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
},

{
    "NAME":
        "django.contrib.auth.password_validation.MinimumLengthValidator",
},

{
    "NAME":
        "django.contrib.auth.password_validation.CommonPasswordValidator",
},

{
    "NAME":
        "django.contrib.auth.password_validation.NumericPasswordValidator",
},

]

# ==================================================

# INTERNATIONALIZATION

# ==================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# ==================================================

# CUSTOM USER

# ==================================================

AUTH_USER_MODEL = "xcoin.User"

# ==================================================

# LOGIN

# ==================================================

LOGIN_URL = "login"

LOGIN_REDIRECT_URL = "dashboard"

LOGOUT_REDIRECT_URL = "login"

# ==================================================

# STATIC FILES

# ==================================================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [


BASE_DIR / "static",


]

# ==================================================

# STORAGE

# ==================================================

STORAGES = {


# ----------------------------------------------
# USER UPLOADS → CLOUDINARY
# ----------------------------------------------

"default": {

    "BACKEND": "django.core.files.storage.FileSystemStorage",

},


# ----------------------------------------------
# STATIC FILES → WHITENOISE
# ----------------------------------------------

"staticfiles": {

    "BACKEND":
        "whitenoise.storage.CompressedManifestStaticFilesStorage",

},


}

# ==================================================

# ==================================================
# CLOUDINARY
# ==================================================




# MEDIA

# ==================================================

# Cloudinary handles the actual media storage.

#

# Keep these for compatibility with Django code

# that may reference MEDIA_URL / MEDIA_ROOT.

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"

# ==================================================

# EMAIL

# ==================================================

EMAIL_BACKEND = (
"django.core.mail.backends.smtp.EmailBackend"
)

EMAIL_HOST = "smtp.gmail.com"

EMAIL_PORT = 587

EMAIL_USE_TLS = True

EMAIL_HOST_USER = config(
"EMAIL_HOST_USER",
default="",
)

EMAIL_HOST_PASSWORD = config(
"EMAIL_HOST_PASSWORD",
default="",
)

DEFAULT_FROM_EMAIL = config(
"DEFAULT_FROM_EMAIL",
default=EMAIL_HOST_USER,
)

# ==================================================

# DEFAULT PRIMARY KEY

# ==================================================

DEFAULT_AUTO_FIELD = (
"django.db.models.BigAutoField"
)
