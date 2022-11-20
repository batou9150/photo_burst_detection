import logging
import os

from flask import Flask

from photo_burst_detection.scan import Scanner

app = Flask(__name__)
app.config.update({
    'PHOTO_BURST_DETECTION_PATH': os.environ.get('PHOTO_BURST_DETECTION_PATH'),
})

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

scanner = Scanner(
    path=app.config.get('PHOTO_BURST_DETECTION_PATH'),
)

if 1 == 1:
    from photo_burst_detection import views
