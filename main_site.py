import smtplib
import flask_login
from flask import Flask, render_template, redirect
from flask_login import LoginManager, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired

import autorization
import orders

from create_db import session as db_session
from create_db import User, Session

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login = LoginManager()
login.init_app(app)


@login.user_loader
def load_user(user_id):
    db_sess = Session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def hello():
    return redirect('/register')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


if __name__ == "__main__":
    app.register_blueprint(autorization.blueprint)
    app.register_blueprint(orders.blueprint2)
    app.run()
