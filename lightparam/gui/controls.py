import param
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QLineEdit,
    QWidget,
    QVBoxLayout,
    QLabel,
    QCheckBox,
    QGridLayout,
    QSlider,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QHBoxLayout,
)


def pretty_name(paramname: str):
    pn = paramname.capitalize()
    pn = pn.replace("_", " ")
    return pn


class Control(QWidget):
    def __init__(self, parametrized, name):
        super().__init__()
        self.parametrized = parametrized
        self.param = parametrized.params[name]
        self.param_name = name
        self.label = QLabel(pretty_name(name))


class ControlSpin(Control):
    def __init__(self, parametrized, name):
        super().__init__(parametrized, name)
        if isinstance(parametrized.params[name].value, float):
            self.control = QDoubleSpinBox()
        else:
            self.control = QSpinBox()
        # if limits are set, put them in
        self.control.setValue(self.param.value)
        try:
            self.control.setMinimum(self.param.limits[0])
            self.control.setMaximum(self.param.limits[1])
        except TypeError:
            pass
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.control)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.control.valueChanged.connect(self.update_param)

    def update_display(self):
        self.control.setValue(self.param.value)

    def update_param(self):
        setattr(self.parametrized, self.param_name, self.control.value())


class ControlCheck(Control):
    def __init__(self, parametrized, name):
        super().__init__(parametrized, name)
        self.control = QCheckBox()
        # if limits are set, put them in
        self.control.setChecked(param.value)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.control)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.control.clicked.connect(self.update_param)

    def update_display(self):
        self.control.setValue(self.param.value)

    def update_param(self):
        setattr(self.parametrized, self.param_name, self.control.isChecked())


class ControlCombo(Control):
    def __init__(self, parametrized, name):
        super().__init__(parametrized, name)
        self.control = QComboBox()

        self.control.setCurrentText(str(self.param.value))
        self.control.addItems([str(it) for it in self.param.limits])

        self.item_type = type(self.param.value)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.control)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.control.currentTextChanged.connect(self.update_param)
        self.control.setEditable(self.param.editable)

    def update_display(self):
        self.control.setCurrentText(str(self.param.value))

    def update_param(self):
        setattr(self.parametrized, self.param_name, self.control.currentText())


class ControlText(Control):
    def __init__(self, parametrized, name):
        super().__init__(parametrized, name)
        self.control = QLineEdit()

        self.control.setText(str(self.param.value))

        self.item_type = type(self.param.value)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.control)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.control.textChanged.connect(self.update_param)

    def update_display(self):
        self.control.setText(str(self.param.value))

    def update_param(self):
        setattr(self.parametrized, self.param_name, self.item_type(self.control.text()))


class ParameterControl(QWidget):
    """
    Class for the single parameters controls of the metadata GUI
    """

    def __init__(self, parameterized_obj, name, *args, **kwargs):
        """ Constructor
        :param parameterized_obj: parameterized object containing the desired parameter
        :param name: name of the parameter (string)
        """
        # Note: here the parameterized object has to be passed because the
        # parameter object itself seems not to contain its current value,
        # only the default one.

        super().__init__(*args, **kwargs)
        parameter_obj = parameterized_obj.params(name)
        assert isinstance(parameter_obj, param.Parameter)  # Check input

        self.name = name
        self.label = self._pretty_print(name)
        self.parameter = parameter_obj
        self.parameter_val = getattr(parameterized_obj, name)
        self.layout = None
        self.set_layout()
        self.layout.setContentsMargins(0, 0, 0, 5)

    def set_layout(self):
        # Create layout and add label to the control:
        self.layout = QVBoxLayout()

        self.setLayout(self.layout)
        self.widget_label = QLabel(self.label)
        self.layout.addWidget(self.widget_label)

        # Create control widget according to parameter type:
        self.control_widget = self.create_control_widget()
        self.layout.addWidget(self.control_widget)

    def get_value(self):
        pass

    def create_control_widget(self):
        pass

    @staticmethod
    def _pretty_print(s):
        n = s.replace("_", " ")
        n = n.capitalize()
        return n


class StaticControl(ParameterControl):
    """ Widget for unmodifiable parameters
    """

    def create_control_widget(self):
        control_widget = QLineEdit(str(self.parameter_val))
        control_widget.setReadOnly(True)

        # Display this widget in gray:
        control_widget.setStyleSheet("background-color: gray")

        return control_widget

    def get_value(self):
        return self.parameter_val


class BooleanControl(ParameterControl):
    """ Widget for booleans

    """

    def create_control_widget(self):
        control_widget = QCheckBox()
        control_widget.setChecked(self.parameter_val)

        return control_widget

    def get_value(self):
        return self.control_widget.isChecked()


class NumericControlSliderCombined(ParameterControl):
    """ Widget for float parameters
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.numeric_control_widget.setText(str(round(self.parameter_val, 4)))
        self.update_slider()
        self.control_widget.sliderMoved.connect(self.update_numeric)
        self.numeric_control_widget.editingFinished.connect(self.update_slider)

    def set_layout(self):
        # Create layout and add label to the control:
        self.layout = QGridLayout()
        self.widget_label = QLabel(self.label)
        self.layout.addWidget(self.widget_label, 0, 0)

        # Create control widget according to parameter type:
        self.control_widget = self.create_control_widget()
        self.layout.addWidget(self.control_widget, 1, 0, 1, 2)

        self.numeric_control_widget = self.create_numeric_control_widget()
        self.layout.addWidget(self.numeric_control_widget, 0, 1)

        self.setLayout(self.layout)

    def create_control_widget(self):
        slider_control_widget = QSlider(Qt.Horizontal)
        slider_control_widget.setValue(
            int(
                (
                    -self.parameter.bounds[0]
                    + self.parameter_val
                    / (self.parameter.bounds[1] - self.parameter.bounds[0])
                    * 1000
                )
            )
        )
        slider_control_widget.setMaximum(1000)

        return slider_control_widget

    def create_numeric_control_widget(self):
        numeric_control_widget = QLineEdit(str(self.parameter_val))
        # validator = QDoubleValidator(*self.parameter.bounds, 3)
        # control_widget.setValidator(validator)
        return numeric_control_widget

    def update_numeric(self):
        val = self.get_slider_value()
        self.numeric_control_widget.setText(str(round(val, 4)))

    def update_slider(self):
        val = self.get_numeric_value()
        self.control_widget.setValue(
            int(
                (
                    -self.parameter.bounds[0]
                    + val / (self.parameter.bounds[1] - self.parameter.bounds[0]) * 1000
                )
            )
        )

    def get_slider_value(self):
        val = self.parameter.bounds[0] + self.control_widget.value() / 1000 * (
            self.parameter.bounds[1] - self.parameter.bounds[0]
        )
        return val

    def get_numeric_value(self):
        try:
            float(self.numeric_control_widget.text())
        except ValueError:
            self.update_numeric()
        return float(self.numeric_control_widget.text())

    def get_value(self):
        return self.get_numeric_value()


class NumericControl(ParameterControl):
    """ Widget for float parameters
    """

    def create_control_widget(self):
        control_widget = QLineEdit(str(self.parameter_val))

        # TODO Add validator
        # validator = QDoubleValidator(*self.parameter.bounds, 3)
        # control_widget.setValidator(validator)
        return control_widget

    def get_value(self):
        return float(self.control_widget.text())


class NumericControlSlider(ParameterControl):
    """ Widget for float parameters
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.control_widget.valueChanged.connect(self.update_label)
        self.update_label()

    def create_control_widget(self):
        control_widget = QSlider(Qt.Horizontal)
        control_widget.setValue(
            int(
                (
                    -self.parameter.bounds[0]
                    + self.parameter_val
                    / (self.parameter.bounds[1] - self.parameter.bounds[0])
                    * 1000
                )
            )
        )
        control_widget.setMaximum(1000)

        return control_widget

    def get_value(self):
        return self.parameter.bounds[0] + self.control_widget.value() / 1000 * (
            self.parameter.bounds[1] - self.parameter.bounds[0]
        )

    def update_label(self):
        self.widget_label.setText(self.label + " {:.2f}".format(self.get_value()))


class IntegerControl(ParameterControl):
    """ Widget for integer parameters
        """

    def create_control_widget(self):
        control_widget = QLineEdit(str(self.parameter_val))

        # TODO Add validator
        # validator = QIntValidator(*self.parameter.bounds)
        # control_widget.setValidator(validator)
        return control_widget

    def get_value(self):
        return int(self.control_widget.text())


class StringControl(ParameterControl):
    """ Widget for string parameters
    """

    def create_control_widget(self):
        control_widget = QLineEdit(str(self.parameter_val))
        return control_widget

    def get_value(self):
        return self.control_widget.text()


class ListControl(ParameterControl):
    """ Widget for listselect parameters
    """

    def create_control_widget(self):
        control_widget = QComboBox()

        if not self.parameter.check_on_set:
            control_widget.setEditable(True)
        # Add list and set default:
        control_widget.addItems(self.parameter.objects)
        control_widget.setCurrentIndex(control_widget.findText(self.parameter_val))

        return control_widget

    def get_value(self):
        return self.control_widget.currentText()