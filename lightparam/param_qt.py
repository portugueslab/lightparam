from lightparam import Parametrized, Param, ParameterTree
from lightparam.gui import ParameterGui
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QLayout
from PyQt5.QtCore import pyqtSignal, QObject


class ParametrizedQt(Parametrized, QObject):
    sig_param_changed = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.block_signal = False

    def __setattr__(self, item, value):
        super().__setattr__(item, value)
        if hasattr(self, "params"):
            try:
                assert isinstance(self.__dict__[item], Param)
                if not getattr(self, "block_signal", False):
                    self.sig_param_changed.emit({item: value})
            except (KeyError, AssertionError):
                pass


class ParametrizedWidget(Parametrized, QWidget):
    sig_param_changed = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.block_signal = False

    def __setattr__(self, item, value):
        super().__setattr__(item, value)
        if hasattr(self, "params"):
            try:
                assert isinstance(self.__dict__[item], Param)
                if not getattr(self, "block_signal", False):
                    self.sig_param_changed.emit({item: value})
            except (KeyError, AssertionError):
                pass


if __name__ == "__main__":
    from lightparam import ParameterTree

    app = QApplication([])

    class TestParametrized1(ParametrizedWidget):
        def __init__(self, **kwargs):
            super().__init__(name="a/gino", **kwargs)
            self.random = 5
            self.a = Param(1)
            self.b = Param(2.0)
            self.c = Param(5)
            self.a_list = Param("a", ["a", "b", "c"])
            self.sig_param_changed.connect(self.update_param)
            # self.show()

        def update_param(self):
            """Calculate mm/px from calibrator length"""
            if self.c is not None:
                self.block_signal = True
                self.c = self.a / self.b
                self.block_signal = False

    class TestParametrized2(ParametrizedQt):
        def __init__(self, **kwargs):
            super().__init__(name="b/c/pino", **kwargs)
            self.an_int = Param(4)
            self.a_float = Param(1.0, (-1.0, 10.0))

    p = ParameterGui(TestParametrized1())
    p.show()
    app.exec_()
