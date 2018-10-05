from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QPushButton
from lightparam.gui.controls import *
from lightparam import Parametrized, Param

gui_map = dict(
    spin=ControlSpin, check=ControlCheck, combo=ControlCombo, text=ControlText
)


class ParameterGui(QWidget):
    """ A QT gui for a parametrized class

    """

    def __init__(self, parameterized):
        super().__init__()
        self.paramatrized = parameterized
        self.inner_layout = QVBoxLayout()
        self.setLayout(self.inner_layout)
        self.param_widgets = {}
        for name in self.paramatrized.params.items().keys():
            widget = self.make_widget(parameterized, name)
            self.param_widgets[name] = widget
            self.inner_layout.addWidget(widget)

        self.btnPrint = QPushButton("Print")
        self.btnPrint.clicked.connect(self.print_params)
        self.inner_layout.addWidget(self.btnPrint)

    def make_widget(self, parametrized, name):
        try:
            return gui_map[parametrized.params[name].gui](parametrized, name)
        except KeyError:
            raise Exception("Trying to build gui for an unsupported type ", param.gui)

    def print_params(self):
        print(self.paramatrized.params.values)


class TestParametrized(Parametrized):
    def __init__(self):
        super().__init__()
        self.an_int = Param(1)
        self.a_float = Param(1.0, (-1.0, 10.0))
        self.a_str = Param("strstr")
        self.a_list = Param("a", ["a", "b", "c"])


if __name__ == "__main__":

    k = TestParametrized()
    app = QApplication([])
    print(k.params["a_str"])
    p = ParameterGui(k)
    p.show()
    app.exec_()
