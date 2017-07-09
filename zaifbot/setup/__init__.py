from zaifbot.models import Base


def init_database():
    Base.metadata.create_all()