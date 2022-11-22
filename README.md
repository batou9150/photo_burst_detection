# photo_burst_detection

## install

```shell
git clone https://gitlab.com/batou9150/photo_burst_detection.git
cd photo_burst_detection
python3 setup.py install
```

## run

### Run with gunicorn (Unix)

```shell
pip3 install gunicorn

export PHOTO_BURST_DETECTION_PATH=<start path>
export LDAP_HOST=ad.mydomain.com
export LDAP_BASE_DN=dc=mydomain,dc=com

gunicorn -b 0.0.0.0:8000 photo_burst_detection:app
```

### Run with waitress (Windows)

```shell
export PHOTO_BURST_DETECTION_PATH=<start path>
export LDAP_HOST=ad.mydomain.com
export LDAP_BASE_DN=dc=mydomain,dc=com

waitress-serve --listen=*:8000 photo_burst_detection:app
```

## configuration

| variable                   | description           |
|----------------------------|-----------------------|
| PHOTO_BURST_DETECTION_PATH | start path            |
| SECRET_KEY                 | 'secret'              |
| LDAP_HOST                  |                       |
| LDAP_BASE_DN               |                       |
| LDAP_USER_DN               |                       |
| LDAP_GROUP_DN              |                       |
| LDAP_USER_RDN_ATTR         | 'uid'                 |
| LDAP_USER_LOGIN_ATTR       | 'uid'                 |
| LDAP_BIND_USER_DN          |                       |
| LDAP_BIND_USER_PASSWORD    |                       |
| LDAP_GROUP_OBJECT_FILTER   | '(objectclass=group)' |
