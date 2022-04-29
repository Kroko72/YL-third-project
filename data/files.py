import sqlalchemy
from .db_session import SqlAlchemyBase


class File(SqlAlchemyBase):
    __tablename__ = 'files'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.Text, nullable=True, default="")
    filename = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    category = sqlalchemy.Column(sqlalchemy.String)
    filelink = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    pinned = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=False)
