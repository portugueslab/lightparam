from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QPushButton
from lightparam.gui.controls import *
from lightparam.gui.precisionslider import RangeSliderWidgetWithNumbers
from lightparam import Parametrized, Param

gui_map = dict(
    spin=ControlSpin,
    check=ControlCheck,
    combo=ControlCombo,
    text=ControlText,
    range_slider=RangeSliderWidgetWithNumbers,
)


class ParameterGui(QWidget):
    """ A QT gui for a parametrized class

    """

    def __init__(self, parameterized):
        super().__init__()
        self.paramatrized = parameterized
        self.inner_layout = QVBoxLayout()
        self.inner_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.inner_layout)
        self.param_widgets = {}
        for name in self.paramatrized.params.items().keys():
            widget = self.make_widget(parameterized, name)
            if widget is None:
                continue
            self.param_widgets[name] = widget
            self.inner_layout.addWidget(widget)

    def make_widget(self, parametrized, name):
        gui_type = parametrized.params[name].gui
        if gui_type is None:
            return
        try:
            return gui_map[gui_type](parametrized, name)
        except KeyError:
            raise Exception(
                "Trying to build gui for an unsupported type ",
                parametrized.params[name].gui,
            )

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
