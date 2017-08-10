import itertools


class Observed:
    def __init__(self):
        self.__observers = set()

    def obsrevers_add(self, observer, *observers):
        for observer in itertools.chain((observer, ), observers):
            self.__observers.add(observer)
            observer.update()

    def observer_discard(self, observer):
        self.__observers.discard(observer)

    def observers_notify(self):
        for observer in self.__observers:
            observer.update(self)


class SliderModel(Observed):
    def __init__(self, minimum, value, maximum):
        super().__init__()
        self.__minimum = self.__value = self.__maximum = None
        self.minimum = minimum
        self.value = value
        self.maximum = maximum

    @property
    def value(self):
        return self.__value