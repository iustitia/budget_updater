import datetime
import os

import yaml
from flask import Flask, render_template, url_for, flash
from flask_login import login_required, LoginManager, login_user, current_user, logout_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import StringField, SelectField, DateField, DecimalField
from wtforms.validators import DataRequired, NumberRange

from .google_api import Api


app = Flask(__name__)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE_DIR, 'google_api', 'key.yaml'), 'r') as y:
    config = yaml.load(y)

app.config.update(dict(
    SECRET_KEY=config['SECRET_KEY'],
    WTF_CSRF_SECRET_KEY=config['WTF_CSRF_SECRET_KEY'],
    SQLALCHEMY_DATABASE_URI = config['DATABASE_URL'],
    SQLALCHEMY_TRACK_MODIFICATIONS = False
))

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/', methods=['GET', 'POST'])
@login_required
def main():
    api = Api()

    form = MyForm()
    categories = api.get_categories()
    category_choices = [(value, label) for (label, value) in categories.items()]
    form.category.choices = category_choices
    if form.validate_on_submit():
        category = form.category.data
        date = form.date.data
        value = form.value.data
        api.update_expense_by_cat_id(category, value, date)
        return redirect(url_for('.main', message='Data updated!'))
    else:
        pass
    return render_template('index.html', form=form)


@app.route('/update')
def update():
    return 'Hello, updated World!'


class LoginForm(FlaskForm):
    username = StringField('login', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])


@app.route('/login', methods=['GET', 'POST'])
def login():
    from .models import User
    if current_user.is_authenticated:
        return redirect(url_for('.main'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user)

        return redirect(url_for('.main'))
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


class MyForm(FlaskForm):
    category = SelectField('category', validators=[DataRequired()], coerce=int)
    name = StringField('name', validators=[DataRequired()], default='your name')
    date = DateField('date', format='%d.%m.%Y', validators=[DataRequired()], default=datetime.datetime.today())
    value = DecimalField('money', validators=[DataRequired(), NumberRange(min=0, max=10000)])


if __name__ == '__main__':
    app.run(debug=False)

