import itertools


class Observable:
    def __init__(self):
        self.__observers = set()

    def register_observers(self, observer, *observers, update=False):
        for observer in itertools.chain((observer, ), observers):
            self.__observers.add(observer)

            if update is True:
                observer.update(self)

    def remove_observers(self, observer):
        self.__observers.discard(observer)

    def notify_observers(self):
        for observer in self.__observers:
            observer.update(self)
