class ImproperlyConfigured(Exception):
    pass


class Error400(Exception):
    message = "Bad request"


class Error403(Exception):
    message = "Forbidden"


class Error503(Exception):
    message = "Service Unavailable"


class TodoDoesNotExist(Error400):
    message = "Todo does not exist"
