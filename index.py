import os
import secrets
import string
from datetime import timedelta
from flask import render_template, Flask, request
from flask_login import login_required, logout_user, LoginManager, login_user, current_user
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from data import db_session
from data.constants import key, cookie_lifetime, MAILSALT
from data.entry import Entry
from data.forms import RegisterForm, LoginForm, EntriesForm, FilesForm, PasswordRecoverForm
from data.users import User
from data.send_email import send_email
from data.not_confirmed_user import NotConfirmedUser
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from data.db_functions import pin_something, delete_something
from data.files import File
from data import Users_api


app = Flask(__name__)
app.config['SECRET_KEY'] = key
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=cookie_lifetime)  # Время жизни куки
login_manager = LoginManager()
login_manager.init_app(app)
url_for_token = URLSafeTimedSerializer(app.config["SECRET_KEY"])

db_session.global_init("db/narod.db")  # Подключение к базе данных


# Главная страница с записями
@app.route("/")
def main_page():
    db_sess = db_session.create_session()
    entries = db_sess.query(Entry)  # Все записи
    pinned_entries = db_sess.query(Entry).filter(Entry.pinned == True)  # Закреплённые записи
    return render_template("main_page.html", entries=entries, title="Licey83narod", pinned_entries=pinned_entries)


# Добавление записей
@app.route('/add_entry', methods=['GET', 'POST'])
@login_required
def add_entry():
    if current_user.id == 1:
        form = EntriesForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            entry = Entry()
            entry.title = form.title.data
            entry.content = form.content.data
            entry.images = ""  # В базе данных хранится название картинок с расширением через пробел

            if request.files.getlist("images")[0].filename:  # Проверка на то, что была загружена хоть одна картинка
                for i in request.files.getlist("images"):
                    i.save(os.path.join('static/img', i.filename))  # Сохранение картинок
                    entry.images += " " + i.filename  # Добавление названия картинки к строке
                entry.images = entry.images.lstrip()  # Обрезание левого пробела

            db_sess.merge(entry)
            db_sess.commit()
            return redirect('/')
        return render_template('/add_entry.html', title='Добавление записи', form=form)
    return render_template("error_page.html", title="Недостаточно прав", error_message="Недостаточно прав")


# Регистрация
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegisterForm()
    if form.validate_on_submit():
        # Если пароли не совпадают
        if form.password.data != form.password_again.data:
            return render_template('registration.html', title='Регистрация', form=form, message="Пароли не совпадают")
        # Проверка на корректный ввод класса
        if int(form.grade.data) < 5 or int(form.grade.data) > 11:
            return render_template('registration.html', title='Регистрация', form=form, message="Указан неверный класс")
        db_sess = db_session.create_session()
        # Если такая почта уже зарегистрирована
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('registration.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        # Отправка письма со ссылкой на подтверждение
        send_email(form.email.data, token=url_for_token.dumps(form.email.data, salt=MAILSALT), type="registration")
        # Хранение данных с форм в таблице неподтверждённых пользователей
        not_confirmed_user = NotConfirmedUser(
            name=form.name.data,
            surname=form.surname.data,
            grade=form.grade.data,
            grade_char=form.grade_char.data,
            email=form.email.data,
        )
        not_confirmed_user.set_password(form.password.data)
        db_sess.add(not_confirmed_user)
        db_sess.commit()
        return render_template("confirm_page.html", success_message="Письмо с ссылкой на подтверждение \
                                                                     отправлено на почту")
    return render_template('registration.html', title='Регистрация', form=form)


# Страница подтверждения регистрации
@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = url_for_token.loads(token, salt=MAILSALT, max_age=60*10)
    except SignatureExpired:
        return render_template("error_page.html", title="Регистрация", error_message="Время действия ссылки истекло")
    db_sess = db_session.create_session()
    not_confirmed_user = db_sess.query(NotConfirmedUser).filter(NotConfirmedUser.email == email)\
        .order_by(NotConfirmedUser.id.desc()).first()
    user = User(
        name=not_confirmed_user.name,
        surname=not_confirmed_user.surname,
        grade=not_confirmed_user.grade,
        grade_char=not_confirmed_user.grade_char,
        email=not_confirmed_user.email,
        hashed_password=not_confirmed_user.hashed_password,
    )
    db_sess.add(user)
    db_sess.commit()
    return render_template("confirm_page.html", title="Вы зарегистрированы!", success_message="Вы зарегистрированы!")


# Вход в аккаунт
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        # Если введённый пароль совпадает с расхэшированным паролем из базы данных
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


# Удаление записи
@app.route('/delete_entry/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_entry(id):
    if current_user.get_id() == "1":  # Удалять может только админ
        db_sess = db_session.create_session()
        entry = db_sess.query(Entry).filter(Entry.id == id).first()  # Получение записи
        delete_something(to_delete=entry, db_sess=db_sess)
        return redirect("/")
    return render_template("error_page.html", title="Недостаточно прав", error_message="Недостаточно прав")


# Редактирование записи
@app.route('/edit_entry/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_entry(id):
    if current_user.get_id() == "1":  # Изменять может только админ
        form = EntriesForm()
        if request.method == "GET":
            db_sess = db_session.create_session()
            entry = db_sess.query(Entry).filter(Entry.id == id).first()
            if entry:
                form.title.data = entry.title
                form.content.data = entry.content
            else:
                abort(404)
        # Если нажата кнопка подтверждения
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            entry = db_sess.query(Entry).filter(Entry.id == id).first()
            # Если запись найдена
            if entry:
                entry.title = form.title.data
                entry.content = form.content.data
                entry.images = ""  # В базе данных хранится название картинок с расширением через пробел

                if request.files.getlist("images")[0].filename:  # Проверка на то, что была загружена хоть одна картинка
                    for i in request.files.getlist("images"):
                        i.save(os.path.join('static/img', i.filename))  # Сохранение картинок
                        entry.images += " " + i.filename  # Добавление названия картинки к строке
                    entry.images = entry.images.lstrip()  # Обрезание левого пробела

                db_sess.commit()
                return redirect('/')
            else:
                abort(404)
        return render_template('add_entry.html', title='Редактирование записи', form=form)
    return render_template("error_page.html", title="Недостаточно прав", error_message="Недостаточно прав")


# Закрепление записи
@app.route('/pin_entry/<int:id>', methods=['GET', 'POST'])
@login_required
def pin_entry(id):
    if current_user.get_id() == "1":  # Закреплять или откреплять может только админ
        db_sess = db_session.create_session()
        entry = db_sess.query(Entry).filter(Entry.id == id).first()  # Получение записи
        pin_something(to_pin=entry, db_sess=db_sess)
        return redirect("/")
    return render_template("error_page.html", title="Недостаточно прав", error_message="Недостаточно прав")


# Страница с файлами
@app.route("/files", methods=['GET', 'POST'])
def files_page():
    db_sess = db_session.create_session()
    files = db_sess.query(File)  # Все записи
    pinned_files = db_sess.query(File).filter(File.pinned == True)  # Закреплённые записи
    return render_template("files_page.html", title="Файлы", files=files, pinned_files=pinned_files)


# Добавление файлов
@app.route('/add_file', methods=['GET', 'POST'])
@login_required
def add_file():
    if current_user.id == 1:
        form = FilesForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            file = File()
            file.title = form.title.data
            file.content = form.content.data
            if form.filename.data:
                file.filename = form.filename.data.filename
                form.filename.data.save(os.path.join('static/files', form.filename.data.filename))  # Сохранение файла
            elif form.filelink.data:
                file.filelink = form.filelink.data
            db_sess.merge(file)
            db_sess.commit()
            return redirect('/files')
        return render_template('/add_file.html', title='Добавление файла', form=form)
    return render_template("error_page.html", title="Недостаточно прав", error_message="Недостаточно прав")


# Закрепление файла
@app.route('/pin_file/<int:id>', methods=['GET', 'POST'])
@login_required
def pin_file(id):
    if current_user.get_id() == "1":  # Закреплять или откреплять может только админ
        db_sess = db_session.create_session()
        file = db_sess.query(File).filter(File.id == id).first()  # Получение записи
        pin_something(to_pin=file, db_sess=db_sess)
        return redirect("/files")
    return render_template("error_page.html", title="Недостаточно прав", error_message="Недостаточно прав")


# Редактирование записи с файлом
@app.route('/edit_file/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_file(id):
    if current_user.get_id() == "1":  # Изменять может только админ
        form = FilesForm()
        if request.method == "GET":
            db_sess = db_session.create_session()
            file = db_sess.query(File).filter(File.id == id).first()
            if file:
                form.title.data = file.title
                form.content.data = file.content
            else:
                abort(404)
        # Если нажата кнопка подтверждения
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            file = db_sess.query(File).filter(File.id == id).first()
            # Если запись найдена
            if file:
                file.title = form.title.data
                file.content = form.content.data
                file.filename = form.filename.data
                db_sess.commit()
                return redirect('/files')
            else:
                abort(404)
        return render_template('add_file.html', title='Редактирование записи с файлом', form=form)
    return render_template("error_page.html", title="Недостаточно прав", error_message="Недостаточно прав")


# Удаление файла
@app.route('/delete_file/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_file(id):
    if current_user.get_id() == "1":  # Удалять может только админ
        db_sess = db_session.create_session()
        file = db_sess.query(File).filter(File.id == id).first()  # Получение записи
        delete_something(to_delete=file, db_sess=db_sess)
        return redirect("/files")
    return render_template("error_page.html", title="Недостаточно прав", error_message="Недостаточно прав")


# Страница восстановления пароля
@app.route("/recover_password", methods=['GET', 'POST'])
def recover_password():
    form = PasswordRecoverForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user:
            password = ''.join(
                secrets.choice(string.ascii_letters + string.digits) for _ in range(10))  # генерация пароля
            send_email(email=user.email, password=password, type="recover_password")  # Отправка нового пароля на почту
            user.set_password(password)  # Установка сгенерированного пароля
            db_sess.commit()
            return render_template("confirm_page.html", title="Восстановление пароля",
                                   success_message="Пароль отправлен на почту")
        else:
            return render_template("error_page.html", title="Восстановление пароля",
                                   error_message="Пользователь с такой почтой не найден")
    return render_template("recover_password.html", title="Восстановление пароля", form=form)


# Обработка ошибки 404 (страница ошибки)
@app.errorhandler(404)
def notFoundPage(error):
    return render_template("error_page.html", title="Страница не найдена", error_message="Страница не найдена")


# Обработка ошибки 401 (страница ошибки)
@app.errorhandler(401)
def mustLogin(error):
    return redirect("/login")


# Обработка ошибки 500 (страница ошибки)
@app.errorhandler(500)
def mustLogin(error):
    return render_template("error_page.html", title="Ошибка сервера", error_message="На сервере произошла ошибка")


# Получение пользователя
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# Выход из аккаунта
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.register_blueprint(Users_api.blueprint)
    app.run()
