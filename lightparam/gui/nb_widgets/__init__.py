import numpy as np
from ipywidgets import (
    IntSlider,
    IntRangeSlider,
    FloatRangeSlider,
    VBox,
    HBox,
    HTML,
    link,
)
from ipycanvas import Canvas, MultiCanvas
from ipyevents import Event
from numba import jit
from traitlets import HasTraits, Tuple
from IPython.display import display
from lightparam import Parametrized, Param, ParameterTree

from .nb_controls import NbookControlIntSlider, NbookControlCheck, \
    NbookControlFloat, NbookControlText, NbookControlCombo

gui_map = dict(
    spin=NbookControlFloat,
    check=NbookControlCheck,
    combo=NbookControlCombo,
    text=NbookControlText,
    #folder=ControlFolder,
    #button=ControlButton,
    #range_slider=RangeSliderWidgetWithNumbers,
)


class NbookParamWidget(HasTraits):
    """ A notebook widget for a parametrized class
    """

    def __init__(self, parameterized):
        super().__init__()
        self.parametrized = parameterized

        ly_items = []
        self.param_widgets = {}
        for name in self.parametrized.params.items().keys():
            control = self.make_widget(parameterized, name)
            if control is None:
                continue
            self.param_widgets[name] = control
            ly_items.append(control)

        self.layout = VBox(ly_items)
        display(self.layout)

    @staticmethod
    def make_widget(parametrized, name):
        gui_type = parametrized.params[name].gui
        if gui_type is None:
            return
        try:
            # print(gui_map[gui_type])
            return gui_map[gui_type](parametrized, name)
        except KeyError:
            raise Exception(
                "Trying to build gui for an unsupported type ",
                parametrized.params[name].gui,
            )
