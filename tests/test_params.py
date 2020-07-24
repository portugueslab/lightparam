import unittest

from lightparam import Parametrized, Param, ParameterTree


class TestBasic(unittest.TestCase):
    def testConstruct(self):
        class TC(Parametrized):
            def __init__(self):
                super().__init__()
                self.x = Param(1.0)
                self.tuple_param = Param((10, 20))

        tc = TC()
        assert tc.x == 1.0
        tc.x = 2.0
        assert tc.x == 2.0
        assert tc.params.x.changed
        tc.params.acknowledge_changes()
        assert not tc.params.x.changed
        setattr(tc, "x", 3.0)
        assert tc.x == 3.0
        assert tc.params.x.changed
        tc.params.acknowledge_changes()
        assert not tc.params.x.changed
        assert tc.params.x.value == 3.0
        assert tc.params["x"].value == 3.0


class TestTree(unittest.TestCase):
    def testConstruct(self):
        class TestParametrized1(Parametrized):
            def __init__(self, **kwargs):
                super().__init__(name="a/gino", **kwargs)
                self.an_int = Param(1)
                self.a_float = Param(1.0, (-1.0, 10.0))
                self.a_str = Param("strstr")
                self.a_list = Param("a", ["a", "b", "c"])

        class TestParametrized2(Parametrized):
            def __init__(self, **kwargs):
                super().__init__(name="b/c/pino", **kwargs)
                self.an_int = Param(4)
                self.a_float = Param(1.0, (-1.0, 10.0))

        tree = ParameterTree()
        paramtrized1 = TestParametrized1(tree=tree)
        paramtrized2 = TestParametrized2(tree=tree)
        dict1 = tree.serialize()
        paramtrized1.an_int = 10
        paramtrized2.a_str = "b"

        assert dict1 != tree.serialize()
        tree.deserialize(dict1)
        assert dict1 == tree.serialize()


class TestParamFunc(unittest.TestCase):
    def testFunc(self):
        def paramfunc(x: Param(0.5), y: Param("ABCDF")):
            return x, y

        p = Parametrized(params=paramfunc)
        assert p.x == 0.5
        assert p.y == "ABCDF"
