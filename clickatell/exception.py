class ClickatellError(Exception):

    def __init__(self, message, code):
        self.message = message
        self.code = code
        Exception.__init__(self, message)
        pass