from flask import Flask, render_template, url_for, flash
from flask_login import login_required, LoginManager, login_user, current_user
from werkzeug.utils import redirect

from webapp import app, LoginForm
from .models import User


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('.main'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)

        return redirect(url_for('.main'))
    return render_template('login.html', form=form)
