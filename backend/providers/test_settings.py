"""
Test settings for availability module
"""
from django.test import TestCase
from django.conf import settings
import os

# Test database configuration
TEST_DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'TEST': {
            'NAME': ':memory:',
        },
    }
}

# Test timezone settings
TEST_TIME_ZONE = 'UTC'
TEST_USE_TZ = True

# Test logging configuration
TEST_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'providers.availability': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Test cache configuration
TEST_CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
