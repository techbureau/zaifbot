class ZaifBotError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)


class InvalidRequest(ZaifBotError):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__(message)

        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['Error'] = {'message': self.message}
        return rv
