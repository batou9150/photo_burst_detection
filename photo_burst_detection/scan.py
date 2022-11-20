import glob
import os
import re
from datetime import datetime, timedelta


class Scanner:
    directories = []

    def __init__(self, path):
        self.path = path
        self.load_directories()

    def get_link(self, path):
        return path.replace(self.path, '').replace('\\', '/')

    def get_fullpath(self, path):
        return os.path.join(self.path, path)

    def load_directories(self):
        self.directories = []
        for root, dirs, files in os.walk(self.path):
            if root != self.path and not root.lower().endswith('video') and len(files) > 0:
                self.directories.append({'name': root,
                                         'link': self.get_link(root),
                                         'path': os.path.join(root, root),
                                         'size': len(files),
                                         })

    def refresh(self):
        self.load_directories()

    def delete_photo(self, path):
        fullpath = self.get_fullpath(path)
        if os.path.isfile(fullpath):
            os.remove(fullpath)
        else:
            raise Exception(str(path) + ' not found or not a file')

    def get_directories(self, f=None):
        return self.directories if f is None else [d for d in self.directories if f in d]

    def get_bursts(self, path, seconds=2):
        prev_date = datetime(1970, 1, 1)
        prev_file = None

        results = [[]]
        for file in sorted(glob.glob(self.get_fullpath(path) + '\\*.jpg', recursive=True)):
            date = extract_date(file)
            if date is None:
                print('WARN ' + file)
                continue
            if date - prev_date < timedelta(seconds=seconds):
                results[-1].append(prev_file)
                results[-1].append(file)
            elif len(results[-1]) > 0:
                results.append([])
            prev_date = date
            prev_file = file

        if len(results[-1]) == 0:
            del results[-1]

        results = sorted(results, key=len, reverse=True)

        return [{
            'id': i,
            'files': [{
                'name': os.path.basename(f),
                'link': '/photo' + self.get_link(f),
                'datetime': extract_date(f).strftime('%d/%m/%Y %H:%M:%S.%f').rstrip('0'),
            } for f in sorted(set(files))],
            'size': len(set(files))} for i, files in enumerate(results)]


def extract_date(s):
    match = re.search(r'_(\d{8}_\d{6,8})', s)
    if not match:
        return None
    sdate = match.group(1)
    return datetime.strptime(sdate, '%Y%m%d_%H%M%S%f')
