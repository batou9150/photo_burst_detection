import glob
import re
import subprocess
import sys
from datetime import datetime, timedelta


def open_image(path):
    cmd = {'linux': 'xdg-open', 'win32': 'explorer', 'darwin': 'open'}[sys.platform]
    subprocess.run([cmd, path])


def get_bursts(path):

    prev_date = datetime(1970, 1, 1)
    prev_file = None

    results = [[]]
    for file in sorted(glob.glob(path + '\\*.jpg', recursive=True)):
        match = re.search(r'_(\d{8}_\d{6,8})', file)
        if not match:
            print('WARN ' + file)
            continue
        sdate = match.group(1)
        date = datetime.strptime(sdate, '%Y%m%d_%H%M%S%f')
        if date - prev_date < timedelta(seconds=2):
            print(file, 'vs', prev_file)
            results[-1].append(prev_file)
            results[-1].append(file)
        elif len(results[-1]) > 0:
            results[-1] = set(results[-1])
            results.append([])
        prev_date = date
        prev_file = file

    if len(results[-1]) == 0:
        del results[-1]

    return results


if __name__ == '__main__':
    bursts = get_bursts(sys.argv[1])
    print('bursts =', len(bursts), 'files =', sum([len(burst) for burst in bursts]))

    counter = 0
    for burst in sorted(bursts, key=len, reverse=True):
        if counter > 20:
            print('please rerun after cleanup')
            break
        for f in burst:
            open_image(f)
            counter += 1
