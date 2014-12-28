class ClickatellError(Exception):
    """
    This error type represents any error we receive from the Clickatell API
    """

    def __init__(self, message, code):
        """
        Construct a new error with a message and code

        :param string message:  The error message
        :param string code:     The error code
        """
        self.message = message
        self.code = code
        Exception.__init__(self, message)
        pass