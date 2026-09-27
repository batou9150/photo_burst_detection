import os
import re
import tempfile

import pytest

# the package reads its configuration and scans the root folder at import time
os.environ['PHOTO_BURST_DETECTION_PATH'] = tempfile.mkdtemp()
os.environ['SECRET_KEY'] = 'test-secret-key'
os.environ['LDAP_HOST'] = 'localhost'

from photo_burst_detection import app, auth, scanner  # noqa: E402

PHOTOS = {
    'a': [
        'IMG_20230101_120000.jpg',
        'IMG_20230101_120001.jpg',  # burst with the previous one (2s)
        'IMG_20230101_120004.jpg',  # burst with the previous one only with 5s
        'IMG_20230101_130000.jpg',
        "IMG_20230101_140000_it's.jpg",
    ],
    'b': [
        'IMG_20230102_100000.jpg',
        'DSC_20230102_100000123.jpg',  # same second, with milliseconds
        'notes.txt',
    ],
}


@pytest.fixture
def library(tmp_path):
    """photo library: <tmp>/root/{a,b}, a sibling root <tmp>/other and a file outside of the root"""
    root = tmp_path / 'root'
    for directory, files in PHOTOS.items():
        (root / directory).mkdir(parents=True)
        for f in files:
            (root / directory / f).touch()
    (tmp_path / 'other' / 'x').mkdir(parents=True)
    (tmp_path / 'other' / 'x' / 'IMG_20230103_100000.jpg').touch()
    (tmp_path / '.hidden').mkdir()
    (tmp_path / 'victim.txt').write_text('do not delete')

    scanner.parent = str(tmp_path)
    scanner.set_path(str(root))
    return tmp_path


@pytest.fixture
def client(library):
    app.config['TESTING'] = True
    return app.test_client()


@pytest.fixture
def logged_client(client):
    auth.save_user('cn=user,dc=test', 'user', {'mail': ['User@Example.com']}, [])
    with client.session_transaction() as session:
        session['_user_id'] = 'cn=user,dc=test'
    return client


@pytest.fixture
def csrf_token(logged_client):
    page = logged_client.get('/').get_data(as_text=True)
    return re.search(r'name="csrf-token" content="([^"]+)"', page).group(1)
