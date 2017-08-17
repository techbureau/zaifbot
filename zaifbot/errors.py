class ZaifBotError(Exception):
    def __init__(self, message):
        self._message = message

    def __str__(self):
        return str(self._message)


# fixme: inherit from zaifboterror
class InvalidRequest(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['Error'] = {'message': self.message}
        return rv
