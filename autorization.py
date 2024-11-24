import flask
from flask import render_template, redirect
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_wtf import FlaskForm
from create_db import User, session, create_engine
from wtforms import PasswordField, BooleanField, SubmitField, EmailField, Form, StringField, SelectField
from wtforms.validators import DataRequired, ValidationError

blueprint = flask.Blueprint(
    'news_api',
    __name__,
    template_folder='templates'
)

email = ""


class LoginForm(FlaskForm):
    username = StringField('ФИО', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class Registration(FlaskForm):
    username = StringField('ФИО', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


@blueprint.route('/register', methods=['GET', 'POST'])
def reg():
    form = Registration()
    if form.submit.data:
        checker = session.query(User).filter(User.username == form.username.data).first()
        if checker:
            return render_template('registration.html', title='Регистрация', message="Такой аккаунт уже существует",
                                   form=form)
        if form.password.data != form.confirm.data:
            return render_template('registration.html', title='Регистрация', message="Пароли не совпадают!",
                                   form=form)
        user = User()
        user.username = form.username.data
        user.password = form.password.data
        user.phone_number = "-"
        user.role = "touroperator"

        session.add(user)
        session.commit()
        return redirect('/login')

    return render_template('registration.html', title='Регистрация', form=form)


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():

        user = session.query(User).filter(User.username == form.username.data).first()
        if user and user.password == form.password.data:
            username = form.username.data
            login_user(user, remember=form.remember_me.data)
            return redirect("/your_orders")

        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Вход', form=form)
