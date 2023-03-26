import sqlalchemy
from data.db_session import SqlAlchemyBase


class Twitter(SqlAlchemyBase):
    __tablename__ = 'twitters'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    discord_nickname = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('accounts.nickname'), nullable=False)
    login = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    phone = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=True)
