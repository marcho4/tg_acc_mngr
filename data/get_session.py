from data import db_session


def get_session(uid):
    db_session.global_init(f"db/main_data_base.db")
    db_sess = db_session.create_session()
    return db_sess
