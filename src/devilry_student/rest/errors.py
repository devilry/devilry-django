from djangorestframework.response import ErrorResponse
from djangorestframework import status


class NotFoundError(ErrorResponse):
    """
    Raised to signal that an item was not found
    """
    def __init__(self, errormsg):
        super(NotFoundError, self).__init__(status.HTTP_404_NOT_FOUND,
                                            {'detail': errormsg})

class BadRequestError(ErrorResponse):
    def __init__(self, errormsg):
        super(BadRequestError, self).__init__(status.HTTP_400_BAD_REQUEST,
                                              {'detail': errormsg})
