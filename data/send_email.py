import smtplib
from email.mime.text import MIMEText
from licey83narod.data.constants import FROM, PASSWORD, HOST, PORT
from email.mime.multipart import MIMEMultipart


# Функция отправки письма
def send_email(email: str, token="", type="", password="") -> None:
    msg = MIMEMultipart()
    msg["From"] = FROM
    msg["To"] = email

    if type == "registration":
        msg["Subject"] = "Licey83narod.ru - подтверждение регистрации"  # Заголовок письма
        body = f"Ссылка для подтверждения: /confirm_email/{token}"  # Текст письма
        msg.attach(MIMEText(body, "plain"))

    elif type == "recover_password":
        msg["Subject"] = "Licey83narod.ru - восстановление пароля"  # Заголовок письма
        body = f"Новый пароль от вашего аккаунта: {password}"  # Текст письма
        msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP_SSL(HOST, PORT)
    server.login(FROM, PASSWORD)  # Вход в почту
    server.send_message(msg)  # Отправка письма
    server.quit()  # Отключение от сервера
