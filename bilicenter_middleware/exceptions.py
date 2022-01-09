class CenterException(Exception):
    def __init__(self, msg, code):
        self.msg = msg
        self.code = code

    def __str__(self):
        return f"{self.msg}[{self.code}]"

    def return_callback(self):
        return dict(msg=self.msg, code=self.code)
