from functools import reduce


def get_nested(d, path):
    return reduce(lambda d, k: d.setdefault(k, {}), path, d)


def set_nested(d, path, value):
    get_nested(d, path[:-1])[path[-1]] = value


def visit_dict(d, path=[]):
    for k, v in d.items():
        if not isinstance(v, dict):
            yield path + [k], v
        else:
            yield from visit_dict(v, path + [k])


class ParamContainer:
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

    def __getitem__(self, item):
        return self.parametrized.__dict__[item]


class ParameterTree:
    """ Class for managing a multi-level tree of parameters

    """
    def __init__(self):  # , categories=(), allow_new_categories=False):
        # self.categories = categories
        self.tracked = dict()
        # self.allow_new_categories = allow_new_categories
        # for cat in self.categories:
        #     self.tracked[cat] = dict()

    def add(self, parametrized):
        #
        # if category not in self.tracked.keys():
        #     if not self.allow_new_categories:
        #         raise Exception("Tying to add ", parametrized.name,
        #                         " parameters to nonexistent category ",
        #                         category)
        #     else:
        #         self.tracked[category] = dict()
        self.tracked[parametrized.name] = parametrized

    # def deserialize(self, restore_dict):
    #     for catname, catdata in restore_dict.items():
    #         for paramsname, paramsdata in catdata.items():
    #             for paramname, paramdata in paramsdata.items():
    #                 try:
    #                     self.tracked[catname][paramsname].params[paramname] = paramdata
    #                 except KeyError:
    #                     pass
    def deserialize(self, restore_dict):
        for k, val in visit_dict(restore_dict):
            try:
                # print(k[-1])
                self.tracked['/'.join(k[:-1])].params[k[-1]].value = val
                # setattr(self.tracked['/'.join(k[:-1])], k[-1], val)
                # self.tracked['/'.join(k[:-1])].params[k[-1]] = val
            except KeyError:
                pass

    def serialize(self):
        new_dict = dict()
        for k in self.tracked.keys():
            set_nested(new_dict, k.split('/'), self.tracked[k].params.values)
        return new_dict

    # def serialize(self):
    #     new_dict = {catname: dict() for catname in self.tracked.keys()}
    #     print(self.tracked)
    #     for category, catdata in self.tracked:
    #         for section, parameterized in catdata:
    #             new_dict[category][section] = parameterized.params.values
    #     return new_dict


class Parametrized(object):
    def __init__(self, name="", category=None, tree=None):
        super().__init__()
        self.name = name
        self.params = ParamContainer(self)
        self.category = category
        if tree is not None:
            tree.add(self)

    def __getattribute__(self, item):
        if isinstance(object.__getattribute__(self, item), Param):
            return object.__getattribute__(self, item).value
        else:
            return object.__getattribute__(self, item)

    def __setattr__(self, item, value):
        if hasattr(self, item):
            if isinstance(object.__getattribute__(self, item), Param):
                object.__getattribute__(self, item).value = value
            else:
                object.__setattr__(self, item, value)
        else:
            object.__setattr__(self, item, value)


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

if __name__ == "__main__":
    class TestParametrized1(Parametrized):
        def __init__(self, **kwargs):
            super().__init__(name='a/gino', **kwargs)
            self.an_int = Param(1)
            self.a_float = Param(1.0, (-1.0, 10.0))
            self.a_str = Param("strstr")
            self.a_list = Param("a", ["a", "b", "c"])

    class TestParametrized2(Parametrized):
        def __init__(self, **kwargs):
            super().__init__(name='b/c/pino', **kwargs)
            self.an_int = Param(4)
            self.a_float = Param(1.0, (-1.0, 10.0))

    tree = ParameterTree()
    paramtrized1 = TestParametrized1(tree=tree)
    paramtrized2 = TestParametrized2(tree=tree)
    dict1 = tree.serialize()
    paramtrized1.an_int = 10

    print(tree.serialize())
    # print('got here')
    tree.deserialize(dict1)
    print(tree.serialize())
