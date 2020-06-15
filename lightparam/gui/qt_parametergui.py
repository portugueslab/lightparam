from PyQt5.QtWidgets import QApplication
from lightparam.gui.controls import *
from lightparam.gui.collapsible_widget import CollapsibleWidget
from lightparam.gui.precisionslider import (
    RangeSliderWidgetWithNumbers,
    SliderWidgetWithNumbers,
)
from lightparam import Parametrized, Param, ParameterTree

gui_map = dict(
    spin=ControlSpin,
    check=ControlCheck,
    combo=ControlCombo,
    text=ControlText,
    folder=ControlFolder,
    button=ControlButton,
    slider=SliderWidgetWithNumbers,
    range_slider=RangeSliderWidgetWithNumbers,
)


class ParameterTreeGui(QWidget):
    def __init__(self, param_tree):
        super().__init__()
        self.param_tree = param_tree
        self.inner_layout = QVBoxLayout()

        self.inner_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.inner_layout)
        self.paramtrized_widgets = {}

        for name in self.param_tree.tracked.keys():
            widget = ParameterGui(self.param_tree.tracked[name])
            self.paramtrized_widgets[name] = widget
            self.inner_layout.addWidget(CollapsibleWidget(widget, name=name))


class ParameterGui(QWidget):
    """ A Qt gui for a parametrized class

    """

    def __init__(self, parameterized, no_margin=False):
        super().__init__()
        self.parametrized = parameterized
        self.inner_layout = QVBoxLayout()
        if no_margin:
            self.inner_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.inner_layout)
        self.param_widgets = {}
        for name in self.parametrized.params.items().keys():
            widget = self.make_widget(parameterized, name)
            if widget is None:
                continue
            self.param_widgets[name] = widget
            self.inner_layout.addWidget(widget)

    @staticmethod
    def make_widget(parametrized, name):
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

    def refresh_widgets(self):
        for name in self.parametrized.params.items().keys():
            if name in self.param_widgets:
                self.param_widgets[name].update_display()


if __name__ == "__main__":

    class TestParametrized(Parametrized):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.an_int = Param(1)
            self.a_float = Param(1.0, (-1.0, 10.0))
            self.a_str = Param("strstr")
            self.a_folder = Param("", gui="folder")
            self.a_list = Param("a", ["a", "b", "c"], editable=False)
            self.a_bool = Param(False, editable=False)
            self.a_range = Param((0.5, 1.5), (0.0, 2.0))
            self.a_different_bool = Param(True, gui=False)

    tree = ParameterTree()
    k = TestParametrized(tree=tree, name="pino")
    app = QApplication([])
    p = ParameterGui(k)
    ti = ControlToggleIcon(
        parametrized=k,
        name="a_different_bool",
        action_on="Turn off",
        action_off="Turn on",
    )
    p.inner_layout.addWidget(ti)
    p.show()
    app.exec_()
