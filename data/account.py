import sqlalchemy
from data.db_session import SqlAlchemyBase


class Account(SqlAlchemyBase):
    __tablename__ = 'accounts'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    nickname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    login = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=False)
    token = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def get_acc_data(self):
        return f'nickname: {self.nickname}\nlogin: {self.login}\npassword: {self.password}\ntoken: {self.token}'
