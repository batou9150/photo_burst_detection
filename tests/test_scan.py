from datetime import datetime

import pytest

from photo_burst_detection import scanner
from photo_burst_detection.scan import extract_date, extract_prefix


@pytest.mark.parametrize('name, expected', [
    ('IMG_20230101_120000.jpg', datetime(2023, 1, 1, 12, 0, 0)),
    ('IMG_20230101_120004.jpg', datetime(2023, 1, 1, 12, 0, 4)),
    ('IMG_20230101_1200001.jpg', datetime(2023, 1, 1, 12, 0, 0, 100000)),
    ('IMG_20230101_12000012.jpg', datetime(2023, 1, 1, 12, 0, 0, 120000)),
    ('/some/dir/DSC_20231231_235959.jpg', datetime(2023, 12, 31, 23, 59, 59)),
    ('holidays.jpg', None),
])
def test_extract_date(name, expected):
    assert extract_date(name) == expected


def test_extract_date_format():
    assert extract_date('IMG_20230101_120000.jpg', '%d/%m/%Y %H:%M:%S') == '01/01/2023 12:00:00'


def test_extract_prefix():
    assert extract_prefix('/dir/IMG_20230101_120000.jpg') == 'IMG'


def test_load_directories(library):
    assert [(d['link'], d['size'], d['bursts']) for d in scanner.get_directories()] == [
        ('/a', 5, 1),
        ('/b', 3, 1),
    ]


def test_get_bursts(library):
    bursts = scanner.get_bursts('a')
    assert len(bursts) == 1
    assert [f['name'] for f in bursts[0]['files']] == ['IMG_20230101_120000.jpg', 'IMG_20230101_120001.jpg']
    assert bursts[0]['files'][0]['link'] == '/photo/a/IMG_20230101_120000.jpg'


def test_get_bursts_wider_window(library):
    bursts = scanner.get_bursts('a', seconds=5)
    assert [f['name'] for f in bursts[0]['files']] == [
        'IMG_20230101_120000.jpg', 'IMG_20230101_120001.jpg', 'IMG_20230101_120004.jpg']


def test_get_bursts_milliseconds(library):
    bursts = scanner.get_bursts('b')
    assert {f['name'] for f in bursts[0]['files']} == {'IMG_20230102_100000.jpg', 'DSC_20230102_100000123.jpg'}


def test_get_folder(library):
    assert [f['name'] for f in scanner.get_folder('b')] == ['IMG_20230102_100000.jpg', 'DSC_20230102_100000123.jpg']


def test_get_namings(library):
    namings = {n['directory']: n for n in scanner.get_namings()}
    assert namings['/a']['prefix'] == {'IMG'}
    assert namings['/b']['prefix'] == {'IMG', 'DSC', 'notes.txt'}
    assert namings['/b']['extension'] == {'.jpg', '.txt'}


def test_get_siblings_lists_visible_directories_only(library):
    assert scanner.get_siblings() == ['other', 'root']


@pytest.mark.parametrize('path', ['../victim.txt', 'a/../../victim.txt', '..\\victim.txt', 'a/../../root2/x'])
def test_get_fullpath_rejects_paths_outside_of_root(library, path):
    with pytest.raises(ValueError):
        scanner.get_fullpath(path)


def test_get_fullpath_keeps_absolute_paths_inside_root(library):
    assert scanner.get_fullpath('/etc/passwd') == str(library / 'root' / 'etc' / 'passwd')


def test_delete_photo(library):
    scanner.delete_photo('a/IMG_20230101_130000.jpg')
    assert not (library / 'root' / 'a' / 'IMG_20230101_130000.jpg').exists()


def test_delete_photo_outside_of_root(library):
    with pytest.raises(ValueError):
        scanner.delete_photo('../victim.txt')
    assert (library / 'victim.txt').exists()


def test_delete_photo_missing(library):
    with pytest.raises(Exception, match='not found'):
        scanner.delete_photo('a/missing.jpg')
