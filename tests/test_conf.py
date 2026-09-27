import os
import subprocess
import sys


def import_conf(**env):
    """import the configuration in a fresh interpreter, as it is read at import time"""
    environ = {k: v for k, v in os.environ.items() if k not in ('SECRET_KEY', 'PHOTO_BURST_DETECTION_CONFIG')}
    environ.update(env)
    return subprocess.run([sys.executable, '-c', 'import photo_burst_detection.conf'],
                          env=environ, capture_output=True, text=True)


def test_secret_key_is_required():
    result = import_conf()
    assert result.returncode != 0
    assert 'SECRET_KEY must be set' in result.stderr


def test_default_secret_key_is_rejected():
    result = import_conf(SECRET_KEY='secret')
    assert result.returncode != 0
    assert 'SECRET_KEY must be set' in result.stderr


def test_secrets_are_masked():
    result = import_conf(SECRET_KEY='my-secret-key', LDAP_BIND_USER_PASSWORD='hunter2', LDAP_HOST='ldap.test')
    assert result.returncode == 0
    assert 'my-secret-key' not in result.stdout
    assert 'hunter2' not in result.stdout
    assert 'SECRET_KEY=********' in result.stdout
    assert 'LDAP_HOST=ldap.test' in result.stdout


def test_config_file(tmp_path):
    config_file = tmp_path / 'photo.conf'
    config_file.write_text('# comment\nSECRET_KEY=from-file\nLDAP_PORT=636\n')
    result = import_conf(PHOTO_BURST_DETECTION_CONFIG=str(config_file))
    assert result.returncode == 0
    assert 'LDAP_PORT=636' in result.stdout


def test_ldap_port_from_environment():
    assert import_conf(SECRET_KEY='k', LDAP_PORT='636').returncode == 0
