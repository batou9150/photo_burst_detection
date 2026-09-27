import pytest

from photo_burst_detection import scanner


@pytest.mark.parametrize('url', ['/', '/burst/', '/burst/a', '/folder/a', '/naming'])
def test_pages_redirect_to_login_when_anonymous(client, url):
    response = client.get(url)
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/login')


@pytest.mark.parametrize('url', ['/photo/a/IMG_20230101_120000.jpg', '/change-root'])
def test_api_is_unauthorized_when_anonymous(client, url):
    assert client.get(url).status_code == 401


def test_login_page(client):
    page = client.get('/login').get_data(as_text=True)
    assert 'name="csrf_token"' in page


@pytest.mark.parametrize('url', ['/', '/burst/', '/burst/a', '/burst/a?seconds=5', '/folder/a', '/naming',
                                 '/change-root'])
def test_pages(logged_client, url):
    assert logged_client.get(url).status_code == 200


def test_user_gravatar(logged_client):
    page = logged_client.get('/').get_data(as_text=True)
    assert 'user@example.com' in page
    assert 'https://www.gravatar.com/avatar/' in page


def test_get_photo(logged_client):
    assert logged_client.get('/photo/a/IMG_20230101_120000.jpg').status_code == 200


def test_delete_button_escapes_link(logged_client):
    page = logged_client.get('/folder/a').get_data(as_text=True)
    assert 'data-link="/photo/a/IMG_20230101_140000_it&#39;s.jpg" onclick="delete_photo(this, this.dataset.link)"' in page


def test_delete_photo(logged_client, csrf_token, library):
    response = logged_client.delete('/photo/a/IMG_20230101_130000.jpg', headers={'X-CSRFToken': csrf_token})
    assert response.status_code == 204
    assert not (library / 'root' / 'a' / 'IMG_20230101_130000.jpg').exists()


def test_delete_photo_requires_csrf_token(logged_client, library):
    assert logged_client.delete('/photo/a/IMG_20230101_130000.jpg').status_code == 400
    assert (library / 'root' / 'a' / 'IMG_20230101_130000.jpg').exists()


@pytest.mark.parametrize('path', ['..%2Fvictim.txt', 'a/../../victim.txt', '%2E%2E/victim.txt'])
def test_delete_photo_outside_of_root(logged_client, csrf_token, library, path):
    response = logged_client.delete(f'/photo/{path}', headers={'X-CSRFToken': csrf_token})
    assert response.status_code == 500
    assert (library / 'victim.txt').exists()


def test_change_root(logged_client, csrf_token, library):
    response = logged_client.post('/change-root', data={'root': 'other', 'csrf_token': csrf_token})
    assert response.status_code == 302
    assert scanner.path == str(library / 'other')
    assert logged_client.get('/photo/x/IMG_20230103_100000.jpg').status_code == 200


@pytest.mark.parametrize('root', ['/etc', '..', '.hidden', 'root/a', ''])
def test_change_root_only_accepts_siblings(logged_client, csrf_token, library, root):
    response = logged_client.post('/change-root', data={'root': root, 'csrf_token': csrf_token})
    assert response.status_code == 400
    assert scanner.path == str(library / 'root')


def test_change_root_requires_csrf_token(logged_client, library):
    assert logged_client.post('/change-root', data={'root': 'other'}).status_code == 400
    assert scanner.path == str(library / 'root')


def test_refresh(logged_client, csrf_token, library):
    (library / 'root' / 'c').mkdir()
    (library / 'root' / 'c' / 'IMG_20230104_100000.jpg').touch()
    assert logged_client.post('/refresh', data={'csrf_token': csrf_token}).status_code == 302
    assert '/c' in [d['link'] for d in scanner.get_directories()]


def test_refresh_is_post_only(logged_client):
    assert logged_client.get('/refresh').status_code == 405


def test_refresh_requires_csrf_token(logged_client):
    assert logged_client.post('/refresh').status_code == 400
