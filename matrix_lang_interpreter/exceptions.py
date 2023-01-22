class ReturnValueException(Exception):
    def __init__(self, values):
        self.values = values

class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass
