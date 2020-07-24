from functools import reduce
from .param_traits import HasTraitsLinked
import warnings


def get_nested(d, path):
    """
    Get value from a nested dictionary, addressing it via a list of keys
    indicating the value to the path.

    Example::

        >>> d = dict(a=dict(a0=0, a1=1))
        >>> get_nested(d, ['a', 'a1'])
        1

    If the path points to an undefined branch in the hierarchy, all required
    nested keys are added to the dictionary and an empty dictionary is added
    as value at that location.

    Example:

        >>> d = dict(a=dict(a0=0, a1=1))
        >>> get_nested(d, ['a', 'a2', 'new_dict'])
        >>> print(d)
        {'a': {'a0': 0, 'a1': 1, 'a2': {'new_dict': {}}}}


    :param d: nested dictionary to address;
    :param path: list of keys forming the path to the required entry;
    :return: entry from addressed path.
        """
    return reduce(lambda d, k: d.setdefault(k, {}), path, d)


def set_nested(d, path, value):
    """
    Set value in a nested dictionary in an arbitrary existing or new
    position of the hierarchy.

    Example::

        >>> d = dict(a=dict(a0=0, a1=1))
        >>> set_nested(d, ['a', 'a1'], 0)
        >>> print(d)
        {'a': {'a1': 0, 'a0': 0}}
        >>> set_nested(d, ['a', 'a2', 'new_entry'], 2)
        >>> print(d)
        {'a': {'a1': 0, 'a2': {'new_entry': 2}, 'a0': 0}}

    :param d: nested dictionary to address;
    :param path: list of keys forming the path to the required entry;
    :param value: value to be set;
    """
    get_nested(d, path[:-1])[path[-1]] = value


def visit_dict(d, path=[]):
    for k, v in d.items():
        if not isinstance(v, dict):
            yield path + [k], v
        else:
            yield from visit_dict(v, path + [k])


class IterParamContainer:
    def __init__(self, param_container):
        self._params = param_container.items()
        self._keys = list(self._params)
        self._index = 0

    def __next__(self):
        if self._index < len(self._keys):
            k = self._keys[self._index]
            par = self._params[k]

            self._index += 1
            return k, par

        raise StopIteration


class ParamContainer(object):
    def __init__(self, p):
        self.parametrized = p

    def items(self):
        return {
            name: param
            for name, param in self.parametrized.__dict__.items()
            if isinstance(param, Param)
        }

    @property
    def values(self):
        return {
            name: param.value
            for name, param in self.parametrized.__dict__.items()
            if isinstance(param, Param)
        }

    def changed_values(self):
        return {
            name: param.value
            for name, param in self.parametrized.__dict__.items()
            if isinstance(param, Param) and param.changed
        }

    def acknowledge_changes(self):
        for name, param in self.parametrized.__dict__.items():
            if isinstance(param, Param):
                param.changed = False

    @values.setter
    def values(self, new_values):
        for key, val in new_values.items():
            self.parametrized.__dict__[key].value = val

    def __getattr__(self, item):
        if item in self.parametrized.__dict__.keys():
            return self.parametrized.__dict__[item]
        else:
            raise AttributeError

    def __getitem__(self, item):
        return self.parametrized.__dict__[item]

    def __iter__(self):
        """Returns the Iterator object"""
        return IterParamContainer(self)


class Parametrized(object):
    def __init__(self, name="", tree=None, params=None):
        """ Creates a parameterized class

        :param name: name, with optional path separated by slashes
        :param tree: a parameter-storing tree
        :param params: (optional) a dictionary of params
        """
        super().__init__()
        self.name = name

        # If there are params:
        if params is not None:
            # If params is actually a function with params annotations,
            # make dict:
            if callable(params):
                params = params.__annotations__

            for key, value in params.items():
                if isinstance(value, Param):
                    setattr(self, key, value)

        self.params = ParamContainer(self)

        # If specified, add to a broader tree.
        # Eventual restoring of default parameters happens here:
        if tree is not None:
            tree.add(self)

    def __getattribute__(self, item):
        # If parameter is asked, return its value:
        if isinstance(object.__getattribute__(self, item), Param):
            return object.__getattribute__(self, item).value
        else:
            return object.__getattribute__(self, item)

    def __setattr__(self, item, value):
        # If there is already an attribute by that name:
        if hasattr(self, item):

            # If it is a parameter:
            if isinstance(object.__getattribute__(self, item), Param):

                # If we are replacing with a new parameter:
                if isinstance(value, Param):
                    # If we are over-writing a param with a param, replace all
                    # its properties:
                    for name, attr in value.__dict__.items():
                        object.__getattribute__(self, item).__setattr__(name, attr)

                # Else, just change the parameter value and signal change:
                else:
                    old_val = object.__getattribute__(self, item).value
                    object.__getattribute__(self, item).value = value
                    if old_val != value:
                        object.__getattribute__(self, item).changed = True

            # otherwise, just set:
            else:
                object.__setattr__(self, item, value)

        # otherwise, just set:
        else:
            object.__setattr__(self, item, value)

    def as_hastraits(self):
        return HasTraitsLinked(self)


class Param:
    def __init__(
        self,
        value,
        limits=None,
        desc="",
        gui=None,
        unit="",
        scale=None,
        editable=True,
        loadable=True,
    ):
        """ A parameter

        :param value: default value
        :param limits: minimum and maximum
        :param desc: description of the parameter
        :param gui: preferred gui (spin, slider, combo)
        :param unit: physical unit, if existing
        :param scale: for real-valued parameters linear or logarithmic
        """
        self.value = value
        self.limits = limits
        self.desc = desc
        self.gui = gui
        self.unit = unit
        self.scale = scale
        self.changed = True
        self.editable = editable
        self.loadable = loadable

        # heuristics for gui
        if gui is None:
            if isinstance(self.limits, list):
                self.gui = "combo"
            elif isinstance(self.value, bool):
                self.gui = "check"
            elif isinstance(self.value, int) or isinstance(self.value, float):
                self.gui = "spin"
            elif isinstance(self.value, str):
                self.gui = "text"
            elif isinstance(self.value, tuple):
                if len(self.value) == 2:
                    self.gui = "range_slider"
        elif gui is False:
            self.gui = None


class ParameterTree:
    """ Class for managing a multi-level tree of parameters

    """

    def __init__(self):
        self.tracked = dict()

    def add(self, parametrized):
        """ Add new branched node to the tree.
        :param parametrized:
        :return:
        """
        self.tracked[parametrized.name] = parametrized

    def deserialize(self, restore_dict):
        """ Restore state of the tree based on contents of a restore_dict.
        :param restore_dict: dictionary with the tree state to restore
        :return:
        """
        for k, val in visit_dict(restore_dict):
            try:
                # Get current parameterized object, if present:
                current = self.tracked["/".join(k[:-1])]
                loadable = current.params.items()[k[-1]].loadable

                # If we explicitly made the parameter not loadable from the restoring
                # dictionary, skip. Skip also the restoring of the loadable
                # attribute, which is not loadable itself:
                if not loadable or k[-1] == "loadable":
                    continue

                # try to stop the signal of the parameter has one, to prevent
                # infinite loops:
                try:
                    self.tracked["/".join(k[:-1])].block_signal = True
                except AttributeError:
                    pass

                # Set the actual attribute, if possible:
                setattr(self.tracked["/".join(k[:-1])], k[-1], val)

                # unblock the refresh signal
                try:
                    self.tracked["/".join(k[:-1])].block_signal = False
                except AttributeError:
                    pass

            except KeyError:
                warnings.warn(
                    f"Trying to restore {k}, but it is not present in the parameter tree"
                )

    def serialize(self):
        """ Generate state dict that can be saved to restore the tree.
        """
        new_dict = dict()
        for k in self.tracked.keys():
            set_nested(new_dict, k.split("/"), self.tracked[k].params.values)
        return new_dict
