from traitlets import link, observe
from IPython.display import display
from lightparam.utils import pretty_name

from traitlets import HasTraits, Float, observe, Enum, Int, Bool, Tuple
from ipywidgets import IntSlider, FloatSlider, Checkbox, FloatRangeSlider, \
    Combobox, VBox, HBox, HTML, Dropdown

traits_dict = {int: Int,
               float: Float,
               list: Enum,
               bool: Bool}


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


class TraitWidgRange(TraitWidg):
    def make_widg(self, trait, val):
        return FloatRangeSlider(value=val)


widgets_dict = {Int: TraitWidgInt,
                Float: TraitWidgFloat,
                Enum: TraitWidgCombo,
                Bool: TraitWidgCheck}


class HasTraitsLinked(HasTraits):
    """ API class that instantiate itself as an HasTraits object from a
    Parametrized class.
    Note that (currently) once it is created it does not
    change the values of the Parametrized object it was created from!
    """
    def __init__(self, parametrized):
        self.params = parametrized.params

        # Loop over params and add traits using some heuristics on the Param
        # object value type, and convert arguments
        for k, par in self.params:

            # Ugly trick as par.value for Enum is a list that can't be set as attribute:
            val = par.value
            if type(val) == list:
                val = val[0]

            kwargs = dict(name=k, default_value=val, values=None)
            if type(par.value) == list:
                kwargs["values"] = par.limits
            elif type(par.value) == float or type(par.value) == int:
                if par.limits is not None:
                    (kwargs["min"], kwargs["max"]) = par.limits

            # Use dictionary to get correct traits type:
            trait_type = traits_dict[type(par.value)]

            #
            trait = trait_type(**kwargs)
            self.add_traits(**{k: trait})


    @property
    def values(self):
        return {k: getattr(self, k) for k in self.trait_names()}

            # self.observe(self.trait_changed, k)

            # @staticmethod
            # def trait_changed(trait_change):
            #    self.params[trait_change["name"]].value = trait_change["new"]
            #    print(trait_change)


class HasTraitsWidgetView:
    def __init__(self, has_traits):
        self.has_traits = has_traits

        box_list = []
        for k, trait in has_traits.traits().items():
            widg = widgets_dict[type(trait)](has_traits, k)
            box_list.append(widg)

        self.ipyview = VBox(box_list)

    def _ipython_display_(self):
        display(self.ipyview)