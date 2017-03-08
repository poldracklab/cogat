DEBUG = True

DOMAIN_NAME="http://127.0.0.1"
DOMAIN = "http://ec2-52-40-254-197.us-west-2.compute.amazonaws.com"

#CSRF_COOKIE_SECURE = False
#SESSION_COOKIE_SECURE = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'cogat.db',
    }
}

STATIC_ROOT = 'static/'
STATIC_URL = '/static/'
MEDIA_ROOT = 'assets/'
MEDIA_URL  = '/assets/'
