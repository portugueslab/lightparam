from poparam import Parametrized, Param, ParameterTree
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


# class ParameterTreeQt(ParameterTree):



if __name__ == "__main__":
    from poparam import ParameterTree
    app = QApplication([])
    # p = ParameterGui(k)
    # p.show()

    class TestParametrized1(ParametrizedQt):
        def __init__(self, **kwargs):
            super().__init__(name='a/gino', **kwargs)
            self.an_int = Param(1)
            self.a_float = Param(1.0, (-1.0, 10.0))
            self.a_str = Param("strstr")
            self.a_list = Param("a", ["a", "b", "c"])
            self.sig_param_changed.connect(self.print_change)

        @staticmethod
        def print_change(change_dict):
            print(change_dict)


    class TestParametrized2(ParametrizedQt):
        def __init__(self, **kwargs):
            super().__init__(name='b/c/pino', **kwargs)
            self.an_int = Param(4)
            self.a_float = Param(1.0, (-1.0, 10.0))
            self.sig_param_changed.connect(self.print_change)

        @staticmethod
        def print_change(change_dict):
            print(change_dict)


    tree = ParameterTree()
    paramtrized1 = TestParametrized1(tree=tree)
    paramtrized2 = TestParametrized2(tree=tree)
    dict1 = tree.serialize()
    paramtrized1.an_int = 10
    paramtrized2.a_str = 'b'

    print(tree.serialize())
    tree.deserialize(dict1)
    print(tree.serialize())
    app.exec_()

