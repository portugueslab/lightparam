class Paramcontainer:
    def __init__(self, p):
        self.parametrized = p

    def items(self):
        return {
            name: param
            for name, param in self.parametrized.__dict__.items()
            if isinstance(param, Param)
        }

    @property
    def values(self):
        return {
            name: param.value
            for name, param in self.parametrized.__dict__.items()
            if isinstance(param, Param)
        }

    def __getattr__(self, item):
        return self.parametrized.__dict__[item]


class Parametrized(object):
    def __init__(self):
        super().__init__()
        self.params = Paramcontainer(self)

    def __getattribute__(self, item):
        if isinstance(object.__getattribute__(self, item), Param):
            return object.__getattribute__(self, item).value
        else:
            return object.__getattribute__(self, item)


class Param:
    def __init__(self, value, limits=None, desc="", gui=None, unit="", scale=None, editable=False):
        """ A parameter

        :param value: default value
        :param limits: minimum and maximum
        :param desc: description of the parameter
        :param gui: preferred gui (spin, slider, combo)
        :param unit: phyiscal unit, if existing
        :param scale: for real-valued parameters linear or logarithmic
        """
        self.value = value
        self.limits = limits
        self.desc = desc
        self.gui = gui
        self.unit = unit
        self.scale = scale
        self.editable = editable

        # heuristics for gui
        if gui is None:
            if isinstance(self.limits, list):
                self.gui = "combo"
            elif isinstance(self.value, int) or isinstance(self.value, float):
                self.gui = "spin"
            elif isinstance(self.value, str):
                self.gui = "text"
            elif isinstance(self.value, bool):
                self.gui = "check"


class Paramfunc:
    def __init__(self, func):
        pass
