from traitlets import (
    HasTraits,
    Float,
    observe,
    Enum,
    Int,
    Bool,
    Tuple,
    Unicode,
    TraitType,
)


class FloatRange(TraitType):
    """A trait for an (ip, port) tuple.

    This allows for both IPv4 IP addresses as well as hostnames.
    """

    default_value = (0.5, 0.6)
    min = 0
    max = 1

    def __init__(self, *args, min=0, max=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.min = min
        self.max = max

    def validate(self, obj, value):
        if isinstance(value, tuple):
            if len(value) == 2:
                if value[0] <= value[1]:
                    if value[0] >= self.min:
                        if value[1] <= self.max:
                            return value
        self.error(obj, value)


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

            # heuristics for trait type to use
            if isinstance(par.limits, list):
                trait_type = Enum
                kwargs["values"] = par.limits
            elif isinstance(par.value, bool):
                trait_type = Bool
            elif isinstance(par.value, int):
                if par.limits is not None:
                    (kwargs["min"], kwargs["max"]) = par.limits
                trait_type = Int
            elif isinstance(par.value, float):
                if par.limits is not None:
                    (kwargs["min"], kwargs["max"]) = par.limits
                trait_type = Float
            elif isinstance(par.value, str):
                trait_type = Unicode
            elif isinstance(par.value, tuple):
                if par.limits is not None:
                    (kwargs["min"], kwargs["max"]) = par.limits
                trait_type = FloatRange
            else:
                raise TypeError(f"Param {k} does not have a matching Trait type!")

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
