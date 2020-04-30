from PyQt5.QtCore import Qt, QSize
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
    QPushButton,
    QFileDialog,
    QToolButton,
)

from math import log
from ..utils import pretty_name


class Control(QWidget):
    def __init__(self, parametrized, name):
        super().__init__()
        self.parametrized = parametrized
        self.param = parametrized.params[name]
        self.param_name = name
        self.label = QLabel(pretty_name(name))
        if self.param.desc:
            self.setToolTip(self.param.desc)

        self.setEnabled(self.param.editable)


class ControlSpin(Control):
    def __init__(self, parametrized, name):
        super().__init__(parametrized, name)
        if isinstance(parametrized.params[name].value, float):
            self.control = QDoubleSpinBox()
        else:
            self.control = QSpinBox()
        # if limits are set, put them in
        try:
            self.control.setMinimum(self.param.limits[0])
            self.control.setMaximum(self.param.limits[1])
        except TypeError:
            pass

        if self.param.limits is not None and len(self.param.limits) > 2:
            self.control.setDecimals(int(-round(log(self.param.limits[2]) / log(10))))

        self.control.setValue(self.param.value)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.control)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.control.valueChanged.connect(self.update_param)
        self.control.setSuffix(" " + self.param.unit)

    def update_display(self):
        self.control.setValue(self.param.value)

    def update_param(self):
        setattr(self.parametrized, self.param_name, self.control.value())


class ControlCheck(Control):
    def __init__(self, parametrized, name):
        super().__init__(parametrized, name)
        self.control = QCheckBox()
        # if limits are set, put them in
        self.control.setChecked(self.param.value)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.control)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.control.clicked.connect(self.update_param)

    def update_display(self):
        self.control.setValue(self.param.value)

    def update_param(self):
        setattr(self.parametrized, self.param_name, self.control.isChecked())


class ControlButton(Control):
    def __init__(self, parametrized, name):
        super().__init__(parametrized, name)
        self.control = QPushButton(pretty_name(name))
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.control)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.control.clicked.connect(self.update_param)

    def update_param(self):
        setattr(
            self.parametrized,
            self.param_name,
            not getattr(self.parametrized, self.param_name),
        )


class ControlToggleIcon(QToolButton, Control):
    """A toggle button for a boolean parameter.
    """

    def __init__(
        self,
        parametrized,
        name,
        icon_on=None,
        icon_off=None,
        action_on=None,
        action_off=None,
        icon_size=32,
        **kwargs
    ):
        super().__init__(parametrized=parametrized, name=name)
        self.text_on = action_on or name + " off"
        self.text_off = action_off or action_on or name + " on"
        self.icon_on = icon_on
        self.icon_off = icon_off or self.icon_on
        current_text = self.text_on if self.param.value else self.text_off

        if self.icon_on is None:
            self.setText(current_text)
        else:
            self.setIcon(self.icon_on if self.param.value else self.icon_off)
            self.setToolTip(current_text)
            bs = int(round(icon_size * 1.5))
            self.setFixedSize(QSize(bs, bs))
            self.setIconSize(QSize(icon_size, icon_size))

        self.setCheckable(True)
        self.setChecked(self.param.value)
        self.clicked.connect(self.update_param)

    def update_param(self):
        setattr(self.parametrized, self.param_name, not self.param.value)
        self.update_display()

    def update_display(self):
        if self.icon_on is None:
            self.setText(self.text_on if self.param.value else self.text_off)
        else:
            if not self.param.value:
                self.setIcon(self.icon_off)
                self.setChecked(False)
            else:
                self.setIcon(self.icon_on)
                self.setChecked(True)
            self.setToolTip(self.text_on if self.param.value else self.text_off)


class ControlCombo(Control):
    def __init__(self, parametrized, name):
        super().__init__(parametrized, name)
        self.control = QComboBox()

        self.control.addItems([str(it) for it in self.param.limits])
        self.control.setCurrentText(str(self.param.value))

        self.item_type = type(self.param.value)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.control)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.control.currentTextChanged.connect(self.update_param)

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


class ControlFolder(ControlText):
    def __init__(self, parametrized, name):
        super().__init__(parametrized, name)
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.open_browse_wnd)
        self.layout().addWidget(self.browse_btn)

    def open_browse_wnd(self):
        folder = QFileDialog.getExistingDirectory(
            caption="File to open", directory=None
        )
        self.control.setText(folder)


# Old controls, to be put back in the new framework
class NumericControlSliderCombined:
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


class NumericControl:
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


class NumericControlSlider:
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
