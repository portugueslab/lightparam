

class Paramcontainer:
    def __init__(self, p):
        self.parametrized = p

    def __getattr__(self, item):
        return self.parametrized.__dict__[item]

class Parametrized:
    def __init__(self):
        self.params = Paramcontainer(self)

    def __getattribute__(self, item):
        if isinstance(self.__dict__[item], Param):
            return self.__dict__[item].value
        else:
            return self.__dict__[item]

class Param:
    def __init__(self, value, limits=None, desc="", gui=None):
        self.value = value
        pass
