from flask import render_template, send_from_directory, redirect, url_for, request

from photo_burst_detection import app, scanner


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return render_template('index.html',
                           current=path,
                           directories=scanner.get_directories(),
                           bursts=scanner.get_bursts(path, seconds=int(request.args.get('seconds', '2')))
                           )


@app.route('/refresh')
def refresh():
    scanner.refresh()
    return redirect(url_for('index'))


@app.route('/photo/<path:path>')
def get_photo(path):
    return send_from_directory(scanner.path, path)


@app.route('/photo/<path:path>', methods=["DELETE"])
def delete_photo(path):
    try:
        scanner.delete_photo(path)
        return '', 204
    except Exception as e:
        return e, 500
