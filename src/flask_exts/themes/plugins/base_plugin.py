class BasePlugin:
    def __init__(self, name):
        self.name = name

    def css(self):
        return ""

    def js(self):
        return ""
