from traitlets import link, observe
from IPython.display import display
from lightparam.utils import pretty_name
from ipywidgets import IntSlider, FloatSlider, Checkbox, FloatRangeSlider, \
    Combobox, VBox, HBox, HTML, Dropdown
from traitlets import HasTraits, Float, observe, Enum, Int, Bool, \
    Tuple, Unicode, TraitType
from ..param_traits import FloatRange

class TraitWidg(HBox):
    """ Little horizontal box with label and control for a parameter.
    """
    def __init__(self, has_traits, name):
        self.has_traits = has_traits
        trait = has_traits.traits()[name]

        lab = HTML(f"{pretty_name(name)}:")
        widg = self.make_widg(trait, getattr(self.has_traits, trait.name))
        link((has_traits, name), (widg, 'value'))

        super().__init__([lab, widg])

    def make_widg(self, trait):
        pass


class TraitWidgInt(TraitWidg):
    """ Control for an integer (slider).
    """
    def make_widg(self, trait, val):
        return IntSlider(value=val,
                         min=trait.min, max=trait.max)


class TraitWidgFloat(TraitWidg):
    """ Control for a float (slider).
    """
    def make_widg(self, trait, val):
        return FloatSlider(value=val,
                           min=trait.min, max=trait.max,
                           step=((trait.max - trait.min) / 200))


class TraitWidgCombo(TraitWidg):
    """ Control for"""
    def make_widg(self, trait, val):
        return Dropdown(value=val[0], options=trait.values)


class TraitWidgCheck(TraitWidg):
    def make_widg(self, trait, val):
        return Checkbox(value=val)


class TraitWidgFloatRange(TraitWidg):
    def make_widg(self, trait, val):
        return FloatRangeSlider(value=val, min=trait.min, max=trait.max,
                                step=(trait.max - trait.min) / 200)

widgets_dict = {Int: TraitWidgInt,
                Float: TraitWidgFloat,
                Enum: TraitWidgCombo,
                Bool: TraitWidgCheck,
                FloatRange: TraitWidgFloatRange}


class HasTraitsWidgetView:
    def __init__(self, has_traits):
        self.has_traits = has_traits

        box_list = []
        for k, trait in has_traits.traits().items():
            try:
                widg = widgets_dict[type(trait)](has_traits, k)
                box_list.append(widg)
            except KeyError:
                print(f"No control available for control for trait '{k}'")

        self.ipyview = VBox(box_list)

    def _ipython_display_(self):
        display(self.ipyview)