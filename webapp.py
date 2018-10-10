import datetime
import os

import yaml
from flask import Flask, render_template, url_for
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
    WTF_CSRF_SECRET_KEY=config['WTF_CSRF_SECRET_KEY']
))

api = Api()


@app.route('/', methods=['GET', 'POST'])
def main():

    form = MyForm()
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


class MyForm(FlaskForm):
    categories = api.get_categories()
    category_choices = [(value, label) for (label, value) in categories.items()]

    category = SelectField('category', choices=category_choices, validators=[DataRequired()], coerce=int)
    name = StringField('name', validators=[DataRequired()], default='your name')
    date = DateField('date', format='%d.%m.%Y', validators=[DataRequired()], default=datetime.datetime.today())
    value = DecimalField('money', validators=[DataRequired(), NumberRange(min=0, max=10000)])


if __name__ == '__main__':
    app.run(debug=False)

