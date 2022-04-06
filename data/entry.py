import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Entry(SqlAlchemyBase):
    __tablename__ = 'entries'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    date = str(datetime.datetime.now().date()).split("-")
    time = str(datetime.datetime.now().time()).split(":")
    write_date_time = f"{date[-1]}.{date[1]}.{date[0]} {time[0]}:{time[1]}"
    created_date = sqlalchemy.Column(sqlalchemy.String,
                                     default=write_date_time)
    images = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    pinned = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=False)
