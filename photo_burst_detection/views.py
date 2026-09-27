from flask import render_template, send_from_directory, redirect, url_for, request, abort
from flask_ldap3_login.forms import LDAPLoginForm
from flask_login import current_user, login_user, logout_user

from photo_burst_detection import app, scanner


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect users who are already logged in.
    if current_user and not current_user.is_anonymous:
        app.logger.info('user already logged in')
        return redirect('/')
    form = LDAPLoginForm()
    if form.validate_on_submit():
        app.logger.info(f'login success for {form.user}')
        login_user(form.user)
        return redirect('/')
    form.submit.label.text = 'Sign in'
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/')
def index():
    # Redirect users who are not logged in.
    if not current_user or current_user.is_anonymous:
        return redirect(url_for('login'))

    return render_template('index.html',
                           directories=scanner.get_directories(),
                           path=scanner.path,
                           )


@app.route('/burst/', defaults={'path': ''})
@app.route('/burst/<path:path>')
def burst(path):
    # Redirect users who are not logged in.
    if not current_user or current_user.is_anonymous:
        return redirect(url_for('login'))
    app.logger.info(f'get burst in {path}')
    return render_template('burst.html',
                           current=path,
                           directories=scanner.get_directories(),
                           bursts=scanner.get_bursts(path, seconds=int(request.args.get('seconds', '2'))),
                           )


@app.route('/folder/<path:path>')
def folder(path):
    # Redirect users who are not logged in.
    if not current_user or current_user.is_anonymous:
        return redirect(url_for('login'))
    app.logger.info(f'get burst in {path}')
    return render_template('folder.html',
                           current=path,
                           directories=scanner.get_directories(),
                           folder=scanner.get_folder(path),
                           )


@app.route('/naming')
def naming():
    # Redirect users who are not logged in.
    if not current_user or current_user.is_anonymous:
        return redirect(url_for('login'))

    return render_template('naming.html',
                           namings=scanner.get_namings(),
                           )


@app.route('/refresh', methods=['POST'])
def refresh():
    if not current_user or current_user.is_anonymous:
        return '', 401
    scanner.refresh()
    return redirect(url_for('index'))


@app.route('/change-root')
def change_root_list_sibling():
    if not current_user or current_user.is_anonymous:
        return '', 401
    return render_template('change_root.html',
                           siblings=scanner.get_siblings(),
                           )


@app.route('/change-root', methods=['POST'])
def change_root():
    if not current_user or current_user.is_anonymous:
        return '', 401
    root = request.form.get('root')
    # only allow switching to one of the listed siblings, never an arbitrary path
    if root not in scanner.get_siblings():
        abort(400)
    scanner.set_path(scanner.parent, root)
    return redirect(url_for('index'))


@app.route('/photo/<path:path>')
def get_photo(path):
    if not current_user or current_user.is_anonymous:
        return '', 401
    return send_from_directory(scanner.path, path)


@app.route('/photo/<path:path>', methods=["DELETE"])
def delete_photo(path):
    if not current_user or current_user.is_anonymous:
        return '', 401
    try:
        scanner.delete_photo(path)
        return '', 204
    except Exception as e:
        return str(e), 500
