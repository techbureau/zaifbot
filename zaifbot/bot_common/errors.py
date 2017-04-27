class ZaifBotError(Exception):
    def __init__(self, message):
        self._message = message

    def __str__(self):
        return str(self._message)
