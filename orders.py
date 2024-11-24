import flask
import flask_login
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import not_
from werkzeug.utils import secure_filename

from flask import Flask, render_template, redirect, request, url_for
from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField, Form, StringField, FileField
from wtforms.fields.datetime import DateField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import HiddenField
from wtforms.validators import DataRequired, ValidationError
from main_site import *
from autorization import *
from create_db import *
from wtforms import SelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput

blueprint2 = flask.Blueprint("name", __name__, template_folder="templates")


class Manage_orders(FlaskForm):
    submit = SubmitField("Добавить")
    archive = SubmitField("Архив")


@blueprint2.route('/your_orders', methods=["GET", "POST"])
@login_required
def all_orders():
    form = Manage_orders()
    if form.validate_on_submit():
        return redirect(url_for('blueprintresponse2.add_order'))

    # Сортируем по возрастанию request_id

    user_requests = session.query(Request).filter(
        Request.user_id == current_user.user_id,
        Request.status == 'active'
    ).order_by(Request.request_id.asc()).all()

    return render_template("your_orders.html", title='Ваши заказы', reqs=user_requests, form=form)


@blueprint2.route('/archieve', methods=["GET", "POST"])
@login_required
def archieve():
    # Здесь предполагаем, что статус архивации запроса - "archived"
    archived_requests = session.query(Request).filter(
        Request.user_id == current_user.user_id,
        not_(Request.status == "active")
    ).order_by(Request.request_id.asc()).all()
    buses_info = []
    for req in archived_requests:
        if len(req.status.split("/")) == 3:
            print(req.status.split("/"))
            id, number, price = req.status.split("/")
            response = session.query(Response).filter_by(response_id=id).first()
            bus = session.query(Bus).filter(Bus.bus_id == response.bus_id).first()

            if bus:
                # Получаем номер телефона водителя через user_id
                driver = session.query(User).filter_by(user_id=response.user_id).first()
                phone_number = driver.phone_number if driver else "Нет номера"

                buses_info.append({
                    'bus': bus,
                    'phone_number': phone_number,  # Добавляем номер телефона
                    'price': price
                })

    return render_template("archieve.html", title='Архив', buses_info=buses_info)


class Create_request(FlaskForm):
    start_date = DateField('Начало тура', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('Конец тура', format='%Y-%m-%d', validators=[DataRequired()])
    route = StringField('Маршрут', validators=[DataRequired()])

    transport_types = SelectMultipleField(
        'Типы транспорта',
        choices=[
            ("Минивэны (5-9 мест)", "Минивэны (5-9 мест)"),
            ("Микроавтобусы (10-20 мест)", "Микроавтобусы (10-20 мест)"),
            ("Малые автобусы (21-30 мест)", "Малые автобусы (21-30 мест)"),
            ("Средние автобусы (31-45 мест)", "Средние автобусы (31-45 мест)"),
            ("Большие автобусы (46-60 мест)", "Большие автобусы (46-60 мест)"),
            ("Особо большие автобусы (61-90 мест)", "Особо большие автобусы (61-90 мест)")
        ],
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=False)
    )

    facilities = SelectMultipleField(
        'Удобства и оснащение',
        choices=[
            ("Кондиционер", "Кондиционер"),
            ("Микрофон для гида", "Микрофон для гида"),
            ("Монитор / ТВ", "Монитор / ТВ"),
            ("Откидные кресла", "Откидные кресла"),
        ],
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=False)
    )

    confirm = SubmitField("Отправить")


@blueprint2.route('/add_order', methods=["GET", "POST"], endpoint='add_order')
@login_required
def add():
    form = Create_request()
    if form.confirm.data:
        dct = {
            "Минивэны (5-9 мест)": False,
            "Микроавтобусы (10-20 мест)": False,
            "Малые автобусы (21-30 мест)": False,
            "Средние автобусы (31-45 мест)": False,
            "Большие автобусы (46-60 мест)": False,
            "Особо большие автобусы (61-90 мест)": False
        }

        sec = {
            "Кондиционер": False,
            "Микрофон для гида": False,
            "Монитор / ТВ": False,
            "Откидные кресла": False,
        }
        start_date = form.start_date.data
        end_date = form.end_date.data
        route = form.route.data
        start_date_str = start_date.strftime('%d.%m.%y')
        end_date_str = end_date.strftime('%d.%m.%y')

        data_range = f"{start_date_str}-{end_date_str}"

        for i in form.transport_types.data:
            dct[i] = True

        for i in form.facilities.data:
            sec[i] = True

        new_request = Request(
            user_id=current_user.user_id,
            route=form.route.data,
            date_range=data_range,
            minivan=dct["Минивэны (5-9 мест)"],
            microbus=dct["Микроавтобусы (10-20 мест)"],
            small_bus=dct["Малые автобусы (21-30 мест)"],
            medium_bus=dct["Средние автобусы (31-45 мест)"],
            big_bus=dct["Большие автобусы (46-60 мест)"],
            large_bus=dct["Особо большие автобусы (61-90 мест)"],  # Assuming dct tracks this field
            condition=sec["Кондиционер"],
            microphone_for_guide=sec["Микрофон для гида"],
            monitor=sec["Монитор / ТВ"],
            arm_chairs=sec["Откидные кресла"],
            status="active"
        )

        session.add(new_request)
        session.commit()

        return redirect("/your_orders")
    return render_template("add_order.html", title='Добавление заказа', form=form)


@blueprint2.route('/order/<int:num_order>', methods=["GET", "POST"])
@login_required
def order_details(num_order):
    request_details = session.query(Response).filter_by(request_id=num_order).all()

    # Получаем заказ по num_order
    request_to_update = session.query(Request).filter_by(request_id=num_order).first()

    # Если статус запроса "active", то показываем предложения с кнопками
    if request_to_update and request_to_update.status == "active":
        # Проверка, был ли отправлен response_id
        response_id = request.form.get('response_id')  # Получаем response_id из формы
        if response_id:
            order = session.query(Request).filter_by(request_id=num_order).first()
            date_range = order.date_range
            print(f"Принят отклик с response_id: {response_id}")
            # Создаем новый объект Schedule

            new_schedule = Schedule(
                bus_id=response_id,  # Используем bus_id, который был получен
                date_range=date_range  # Используем date_range из заказа
            )

            # Добавляем новый schedule в базу данных
            session.add(new_schedule)
            session.commit()
            request_to_update.status = "archieve"

            session.commit()
            print(f"Статус заказа {num_order} изменен на 'archieve'.")
            return redirect(f"/order/{num_order}")
        buses_info = []
        for response in request_details:
            bus = session.query(Bus).filter_by(bus_id=response.bus_id).first()  # Получаем автобус по bus_id
            if bus:
                buses_info.append({
                    'bus': bus,
                    'price': response.price,
                    'response_id': response.response_id,  # Добавляем response_id для кнопки
                    'user_id': response.user_id  # Добавляем user_id для получения телефона водителя
                })

        # Возвращаем шаблон с данными
        return render_template("order_details.html", buses_info=buses_info, num_order=num_order, show_phone=False)


    elif request_to_update and request_to_update.status != "active":
        # Создаем список автобусов с откликами, но теперь добавляем номер телефона водителя
        buses_info = []
        for response in request_details:
            bus = session.query(Bus).filter_by(bus_id=response.bus_id).first()  # Получаем автобус по bus_id
            if bus:
                # Получаем номер телефона водителя через user_id
                driver = session.query(User).filter_by(user_id=response.user_id).first()
                phone_number = driver.phone_number if driver else "Нет номера"
                request_to_update.status = f"{response.response_id}/{phone_number}/{response.price}"
                session.commit()
                print(phone_number)
                buses_info.append({
                    'bus': bus,
                    'price': response.price,
                    'phone_number': phone_number  # Добавляем номер телефона
                })

        # Возвращаем шаблон с данными и показываем номер телефона
        return render_template("order_details.html", buses_info=buses_info, num_order=num_order, show_phone=True)

    return redirect(url_for('blueprint2.all_orders'))  # Если не активный заказ, перенаправляем на список всех заказов
