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