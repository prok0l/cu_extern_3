class APIError(Exception):
    pass


class APIAuthorizationError(APIError):
    pass


class APINumberOfRequests(APIError):
    pass
