import logging
import os

from flask import Flask

from photo_burst_detection.scan import Scanner

app = Flask(__name__)
app.config.update({
    'PHOTO_BURST_DETECTION_PATH': os.environ.get('PHOTO_BURST_DETECTION_PATH'),

    'SECRET_KEY': os.environ.get('SECRET_KEY', 'secret'),

    'LDAP_HOST': os.environ.get('LDAP_HOST'),
    'LDAP_BASE_DN': os.environ.get('LDAP_BASE_DN'),
    'LDAP_USER_DN': os.environ.get('LDAP_USER_DN'),
    'LDAP_GROUP_DN': os.environ.get('LDAP_GROUP_DN'),
    'LDAP_USER_RDN_ATTR': os.environ.get('LDAP_USER_RDN_ATTR', 'uid'),
    'LDAP_USER_LOGIN_ATTR': os.environ.get('LDAP_USER_LOGIN_ATTR', 'uid'),
    'LDAP_BIND_USER_DN': os.environ.get('LDAP_BIND_USER_DN'),
    'LDAP_BIND_USER_PASSWORD': os.environ.get('LDAP_BIND_USER_PASSWORD'),
    'LDAP_GROUP_OBJECT_FILTER': os.environ.get('LDAP_GROUP_OBJECT_FILTER', '(objectclass=group)'),
})

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

scanner = Scanner(
    path=app.config.get('PHOTO_BURST_DETECTION_PATH'),
)

if 1 == 1:
    from photo_burst_detection import auth, views
