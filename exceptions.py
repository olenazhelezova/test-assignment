class AppException(Exception):
    pass


class NetworkingException(AppException):
    pass


class ApiClientException(AppException):
    pass


class DataException(AppException):
    pass
