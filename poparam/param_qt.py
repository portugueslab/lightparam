from poparam import Parametrized, Param
from poparam.gui import ParameterGui
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, QObject


class ParametrizedQt(Parametrized, QObject):
    sig_param_changed = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setattr__(self, item, value):
        super().__setattr__(item, value)
        self.sig_param_changed.emit(dict(item=value))


class TestParametrizedQt(ParametrizedQt):
    def __init__(self):
        super().__init__()
        self.an_int = Param(1)
        self.a_float = Param(1.0, (-1.0, 10.0))
        self.a_str = Param("strstr")
        self.a_list = Param("a", ["a", "b", "c"])

if __name__ == "__main__":
    k = TestParametrizedQt()
    app = QApplication([])
    p = ParameterGui(k)
    p.show()
    app.exec_()

