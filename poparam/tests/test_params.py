import unittest

from poparam import Parametrized, Param


class TestBasic(unittest.TestCase):
    def testConstruct(self):
        class TC(Parametrized):
            def __init__(self):
                super().__init__()
                self.x = Param(1.0)

        tc = TC()
        assert tc.x == 1.0
        assert tc.params.x.value == 1.0


class TestParamFunc(unittest.TestCase):
    def testFunc(self):
        def paramfunc(x: Param(0.5), y: Param("ABCDF")):
            return x, y

        print(paramfunc.__annotations__)
        z = paramfunc.__annotations__
        assert paramfunc.__annotations__["x"].value == 0.5
