from flask import render_template, send_from_directory, redirect, url_for, request, render_template_string
from flask_ldap3_login.forms import LDAPLoginForm
from flask_login import current_user, login_user, logout_user

from photo_burst_detection import app, scanner


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LDAPLoginForm()
    if form.validate_on_submit():
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
                           )


@app.route('/burst/', defaults={'path': ''})
@app.route('/burst/<path:path>')
def burst(path):
    # Redirect users who are not logged in.
    if not current_user or current_user.is_anonymous:
        return redirect(url_for('login'))

    return render_template('burst.html',
                           current=path,
                           directories=scanner.get_directories(),
                           bursts=scanner.get_bursts(path, seconds=int(request.args.get('seconds', '2'))),
                           )


@app.route('/refresh')
def refresh():
    if not current_user or current_user.is_anonymous:
        return '', 401
    scanner.refresh()
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
        return e, 500