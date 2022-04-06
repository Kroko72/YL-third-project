from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, StringField, BooleanField, TextAreaField, SelectField, \
                    FileField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    grade = StringField('Номер класса', validators=[DataRequired()])
    grade_char = SelectField("Буква класса", validators=[DataRequired()],  default="A", choices=[("А", "А"),
                                                                                                 ("Б", "Б"),
                                                                                                 ("В", "В"),
                                                                                                 ("Г", "Г")])
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('     Зарегистрироваться     ')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('    Войти    ')


class EntriesForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    images = FileField("Добавить картинки")
    submit = SubmitField('Создать/изменить')


class FilesForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    filename = FileField("Загрузить файл")
    filelink = StringField("Добавить ссылку на файл")
    category = SelectField("Категория", validators=[DataRequired()], default="file", choices=[("file", "Файл"),
                                                                                              ("guide", "Справочник"),
                                                                                              ("program", "Программа")])
    submit = SubmitField('Создать/изменить')


class PasswordRecoverForm(FlaskForm):
    email = StringField("Почта")
    submit = SubmitField("Восстановить пароль")


class TestForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    images = FileField("Загрузить картинки")
    grade = StringField('Номер класса', validators=[DataRequired()])
    grade_char = SelectField("Буква класса", validators=[DataRequired()], default="A", choices=[("А", "А"),
                                                                                                ("Б", "Б"),
                                                                                                ("В", "В"),
                                                                                                ("Г", "Г")])
    submit = SubmitField('Создать/изменить')


class TestAnswerForm(FlaskForm):
    answer = TextAreaField("Ответ:")
    answer_images = FileField("Загрузить картинки")
    submit = SubmitField('Отправить')
