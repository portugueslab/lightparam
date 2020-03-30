import numpy as np
from ipywidgets import (
    IntSlider,
    IntRangeSlider,
    FloatRangeSlider,
    VBox,
    HBox,
    HTML,
    link,
    FloatSlider,
    FloatRangeSlider,
    Text,
    Checkbox,
    FileUpload,
    Combobox
)
from ipycanvas import Canvas, MultiCanvas
from ipyevents import Event
from numba import jit
from traitlets import HasTraits, Tuple
from IPython.display import display
from lightparam import Parametrized, Param, ParameterTree
from ...utils import pretty_name

class NbookControl(HBox):
    def __init__(self, parametrized, name):
        self.parametrized = parametrized
        self.param = parametrized.params[name]
        self.param_name = name

        self.make_control()
        self.control.observe(self.update_from_widg)
        self.control.value = self.param.value
        self.control.description = pretty_name(self.param_name)

        super().__init__([self.control])

        #if self.param.desc:
        #    self.setToolTip(self.param.desc)

        #self.setEnabled(self.param.editable)

    def make_control(self):
        pass

    def _update_param(self, val):
        setattr(self.parametrized, self.param_name, val)

    def update_from_widg(self, *args):
        self._update_param(self.control.value)

    # def update_display(self):
    #     self.control.setVa


class NbookControlIntSlider(NbookControl):
    def make_control(self):
        mn = self.param.limits[0] if self.param.limits else 0
        mx = self.param.limits[1] if self.param.limits else 100
        self.control = IntSlider(min=mn,
                                 max=mx)
        self.control.disabled = True


class NbookControlFloat(NbookControl):
    def make_control(self):
        mn = self.param.limits[0] if self.param.limits else 0
        mx = self.param.limits[1] if self.param.limits else 1
        self.control = FloatSlider(min=mn,
                                   max=mx,
                                   step=0.01)


class NbookControlCheck(NbookControl):
    def make_control(self):
        self.control = Checkbox()


class NbookControlText(NbookControl):
    def make_control(self):
        self.control = Text()


class NbookControlCombo(NbookControl):
    def make_control(self):
        self.control = Combobox()



