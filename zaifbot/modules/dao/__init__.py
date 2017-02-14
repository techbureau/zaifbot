from zaifbot.models import Base, engine, get_session


class DaoBase:
    def __init__(self, model):
        Base.metadata.create_all(bind=engine, tables=[model.__table__])

    @classmethod
    def get_session(cls):
        return get_session()
