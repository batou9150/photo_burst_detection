import os

__envvars = [
    'PHOTO_BURST_DETECTION_PATH',
    'SECRET_KEY',
    'LDAP_HOST',
    'LDAP_PORT',
    'LDAP_BASE_DN',
    'LDAP_USER_DN',
    'LDAP_GROUP_DN',
    'LDAP_USER_RDN_ATTR',
    'LDAP_USER_LOGIN_ATTR',
    'LDAP_BIND_USER_DN',
    'LDAP_BIND_USER_PASSWORD',
    'LDAP_GROUP_OBJECT_FILTER',
]

config = {
    'SESSION_COOKIE_SAMESITE': 'Lax',
    'REMEMBER_COOKIE_SAMESITE': 'Lax',
    # CSRF tokens stay valid for the whole session, so a page left open does not break deletes
    'WTF_CSRF_TIME_LIMIT': None,
}

if 'PHOTO_BURST_DETECTION_CONFIG' in os.environ:
    with open(os.environ['PHOTO_BURST_DETECTION_CONFIG'], 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            try:
                key, value = line.strip().split('=', 1)
                config[key] = value
            except Exception as e:
                print(f'error : {e} on {line}')

for var in __envvars:
    if var in os.environ:
        config[var] = os.environ[var]

if not config.get('SECRET_KEY') or config['SECRET_KEY'] == 'secret':
    raise RuntimeError('SECRET_KEY must be set to a random value, '
                       'e.g. python3 -c "import secrets; print(secrets.token_hex())"')


def __is_secret(key):
    return 'PASSWORD' in key or 'SECRET' in key


print('#####################')
print('### configuration ###')
for k, v in config.items():
    print(f'{k}={"********" if __is_secret(k) else v}')
print('#####################')
