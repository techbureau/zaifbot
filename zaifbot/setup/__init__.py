from zaifbot.models.models import Base


def init_database():
    Base.metadata.create_all()