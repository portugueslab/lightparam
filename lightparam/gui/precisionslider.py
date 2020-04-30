""" A precision slider, designed after the Bauhaus sliders from the Darktable project

"""

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QGridLayout,
    QDoubleSpinBox,
    QLabel,
    QGraphicsOpacityEffect,
)
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, pyqtSignal, QPointF, QPoint

import math
from lightparam import Param, Parametrized
from lightparam.gui.controls import pretty_name, Control


class RangeSliderWidgetWithNumbers(Control, QWidget):
    sig_changed = pyqtSignal(float, float)

    def __init__(self, parametrized, name, precision=2):
        super().__init__(parametrized, name)
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.spin_left = QDoubleSpinBox()
        self.spin_right = QDoubleSpinBox()

        min_val, max_val = parametrized.params[name].limits
        self.left, self.right = parametrized.params[name].value

        for spin in [self.spin_right, self.spin_left]:
            spin.setRange(min_val, max_val)
            spin.setDecimals(precision)
            spin.setSingleStep(10 ** (-precision))

        self.spin_left.setValue(self.left)
        self.spin_right.setValue(self.right)

        self.spin_left.valueChanged.connect(self.update_slider_left)
        self.spin_right.valueChanged.connect(self.update_slider_right)
        self.label_name = QLabel(pretty_name(name))
        self.label_name.setAlignment(Qt.AlignCenter)
        self.grid_layout.addWidget(self.spin_left, 0, 0)
        self.grid_layout.addWidget(self.label_name, 0, 1)
        self.grid_layout.addWidget(self.spin_right, 0, 2)
        self.range_slider = RangeSliderWidget(
            min_val, max_val, left=self.left, right=self.right
        )
        self.grid_layout.addWidget(self.range_slider, 1, 0, 1, 3)
        self.setLayout(self.grid_layout)
        self.range_slider.sig_changed.connect(self.update_values)

        self.update_display()

    def update_values(self, l, r):
        self.spin_left.setValue(l)
        self.spin_right.setValue(r)
        self.sig_changed.emit(l, r)
        self.left, self.right = l, r
        self.update_param()

    def update_slider_left(self, new_val):
        self.range_slider.left = new_val
        self.range_slider.update()
        self.left = new_val
        self.sig_changed.emit(self.range_slider.left, self.range_slider.right)
        self.update_param()

    def update_slider_right(self, new_val):
        self.range_slider.right = new_val
        self.range_slider.update()
        self.right = new_val
        self.sig_changed.emit(self.range_slider.left, self.range_slider.right)
        self.update_param()

    def update_display(self):
        l, r = getattr(self.parametrized, self.param_name)
        self.spin_left.setValue(l)
        self.spin_right.setValue(r)
        self.range_slider.left = l
        self.range_slider.right = r
        self.range_slider.update()

    def update_param(self):
        setattr(self.parametrized, self.param_name, (self.left, self.right))


class SliderWidgetWithNumbers(QWidget):
    sig_changed = pyqtSignal(float)

    def __init__(self, parametrized, name):
        super().__init__()
        self.parametrized = parametrized
        self.param_name = name

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)

        self.spin_val = QDoubleSpinBox()
        self.value = parametrized.params[name].value
        min_val, max_val = parametrized.params[name].limits

        if self.value is None:
            self.value = (min_val + max_val) / 2
        self.spin_val.setValue(self.value)

        self.spin_val.setRange(min_val, max_val)
        self.spin_val.setDecimals(4)
        self.spin_val.setSingleStep(0.001)

        self.spin_val.valueChanged.connect(self.update_slider)

        self.label_name = QLabel(name)
        self.label_name.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.grid_layout.addWidget(self.label_name, 0, 0)
        self.grid_layout.addWidget(self.spin_val, 0, 1)
        self.slider = PrecisionSingleSlider(min_val, max_val, default_value=self.value)
        self.grid_layout.addWidget(self.slider, 1, 0, 1, 2)
        self.setLayout(self.grid_layout)
        self.slider.sig_changed.connect(self.update_values)

    def update_values(self, val):
        self.spin_val.setValue(val)
        self.value = val
        self.sig_changed.emit(val)
        self.update_param()

    def update_slider(self, new_val):
        self.slider.pos = new_val
        self.slider.update()
        self.value = new_val
        self.sig_changed.emit(new_val)
        self.update_param()

    def update_display(self):
        val = getattr(self.parametrized, self.param_name)
        self.slider.pos = val
        self.spin_val.setValue(val)
        self.slider.update()

    def update_param(self):
        setattr(self.parametrized, self.param_name, self.value)


class SliderPopupLines(QWidget):
    """ A widget that displays the guiding lines for the fine adjustment

    """

    def __init__(self, *args, f_line, **kwargs):
        super().__init__(*args, **kwargs)
        self.f_line = f_line
        self.fadeub = QGraphicsOpacityEffect(self)
        self.current_value = 0

    def set_current_value(self, val):
        self.current_value = val
        self.update()

    def paintEvent(self, e):
        size = self.size()
        w = size.width()
        h = size.height()

        halfw = w / 2

        dy = 1

        qp = QPainter()
        qp.begin(self)
        # qp.setRenderHint(QPainter.Antialiasing)

        qp.setPen(Qt.NoPen)
        qp.setBrush(QColor(0, 0, 0, 70))
        qp.drawRoundedRect(0, 0, w, h, 3, 3)

        qp.setPen(QColor(100, 100, 100))

        for xs in [-halfw * 3 / 4, -halfw / 2, -halfw / 4, -halfw / 8, -halfw / 16]:
            for coeff in [-1, 1]:
                x_s = xs * coeff
                x_p = x_s
                y_p = dy
                for y in range(dy * 2, h, dy):
                    x = x_s * self.f_line(y)
                    qp.drawLine(x_p + halfw, y_p, x + halfw, y)
                    x_p = x
                    y_p = y

        x_s = self.current_value
        x_p = x_s
        y_p = 0
        qp.setPen(QColor(250, 250, 250))
        for y in range(dy, h, dy):
            x = x_s * self.f_line(y)
            qp.drawLine(x_p + halfw, y_p, x + halfw, y)
            x_p = x
            y_p = y

        qp.end()


class PrecisionSlider(QWidget):
    def __init__(self, min=0.0, max=1.0, max_magnification=50, magnifier_height=200):
        super().__init__()

        self.min_val = min
        self.max_val = max

        # display geometry
        self.padding_top = 15
        self.padding_side = 0
        self.default_color = QColor(200, 200, 200)
        self.highlight_color = QColor(30, 100, 200)
        self.triangle_size = 8
        self.magnifier_height = magnifier_height
        self.max_magnification = max_magnification
        self.square_coef = (
            1 - 1 / self.max_magnification
        ) / self.magnifier_height ** 1.5

        self.mouse_status = 0
        self.mouse_start_x = 0
        self.mouse_start_y = 0

        self.popup = SliderPopupLines(self, f_line=self.f_line)
        self.popup.setWindowFlags(
            Qt.Tool | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint
        )
        self.popup.setAttribute(Qt.WA_ShowWithoutActivating)
        self.popup.setAttribute(Qt.WA_TranslucentBackground, True)

        self.setMinimumHeight(self.padding_top * 3)

    def _equilateral_triangle_points(self, origin):
        h = self.triangle_size
        w = self.triangle_size / (math.sqrt(3))
        return origin, (origin[0] - w, origin[1] + h), (origin[0] + w, origin[1] + h)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def f_amp(self, y):
        """ Function which maps a y position of the mouse to an amplification factor

        :param y:
        :return:
        """
        # TODO a more reasonable one
        return 1 - self.square_coef * min(y, self.magnifier_height) ** 1.5

    def f_line(self, y):
        """ Function that gives the

        :param coef:
        :param magnifier_height:
        :return:
        """
        return 1 / (1 - self.square_coef * min(y, self.magnifier_height) ** 1.5)

    def val_to_vis(self, val):
        size = self.size()
        w = size.width()
        p = self.padding_side
        return int(
            round(
                p + (w - 2 * p) * (val - self.min_val) / (self.max_val - self.min_val)
            )
        )

    def vis_to_val_relative(self, vis_rel):
        size = self.size()
        w = size.width()
        p = self.padding_side
        return (self.max_val - self.min_val) * vis_rel / (w - 2 * p)

    def vis_to_val(self, vis):
        size = self.size()
        w = size.width()
        p = self.padding_side
        return self.min_val + (self.max_val - self.min_val) * (vis - p) / (w - 2 * p)

    def mouseReleaseEvent(self, QMouseEvent):
        self.mouse_status = 0
        self.popup.hide()
        self.update()


class PrecisionSingleSlider(PrecisionSlider):
    sig_changed = pyqtSignal(float)

    def __init__(self, *args, default_value=None, **kwargs):
        super().__init__(*args, **kwargs)
        if default_value is None:
            self.pos = (self.min_val + self.max_val) / 2
        else:
            self.pos = default_value

        # GUI helpers

        self.triangle = None

        self.bar_shift = 0
        self.old_pos = 0

    def drawWidget(self, qp):
        size = self.size()
        w = size.width()
        h = size.height()
        pt = self.padding_top
        ps = self.padding_side

        qp.setPen(QColor(100, 100, 100))
        qp.drawLine(ps, pt, w - ps, pt)
        qp.setPen(Qt.NoPen)
        qp.setBrush(self.default_color)

        lv = self.val_to_vis(self.pos)

        self.triangle = self._equilateral_triangle_points((lv, pt))

        for triangle, label in zip([self.triangle], [1]):
            if self.mouse_status == label:
                qp.setBrush(self.highlight_color)
            else:
                qp.setBrush(self.default_color)

            qp.drawPolygon(*map(lambda point: QPointF(*point), triangle))

    def mousePressEvent(self, ev):
        self.old_pos = self.pos
        self.mouse_start_x = ev.x()
        self.mouse_start_y = ev.y()
        self.mouse_status = 0
        # check if mouse is pressed on any of the handles
        triangle = self.triangle
        if (triangle[1][0] < self.mouse_start_x < triangle[2][0]) and (
            triangle[0][1] < self.mouse_start_y < triangle[1][1]
        ):
            self.mouse_status = 1
        # check if mose is pressed on the bar
        if self.mouse_status > 0:
            self.mouse_start_y = triangle[1][1]
            self.popup.show()

            global_xy = self.mapToGlobal(QPoint(self.mouse_start_x, self.mouse_start_y))

            self.popup.setGeometry(
                global_xy.x() - self.magnifier_height // 2,
                global_xy.y(),
                self.magnifier_height,
                self.magnifier_height,
            )

    def set_pos_vis(self, visval):
        self.pos = min(self.max_val, max(self.min_val, self.vis_to_val(visval)))

    def mouseMoveEvent(self, ev):
        x = ev.x()
        delta = x - self.mouse_start_x
        amplification = self.f_amp(abs(ev.y() - self.mouse_start_y))

        x_n = self.vis_to_val_relative(delta * amplification)

        if self.mouse_status == 1:
            self.pos = min(max(self.old_pos + x_n, self.min_val), self.max_val)

        self.update()
        self.popup.set_current_value(delta * amplification)
        self.sig_changed.emit(self.pos)


class RangeSliderWidget(PrecisionSlider):
    sig_changed = pyqtSignal(float, float)

    def __init__(self, *args, left=None, right=None, **kwargs):
        super().__init__(*args, **kwargs)
        centre = (self.min_val + self.max_val) / 2
        range = self.max_val - self.min_val
        if right is None:
            self.right = centre + range / 10
        else:
            self.right = right
        if left is None:
            self.left = centre - range / 10
        else:
            self.left = left

        self.barwidth = 2

        # GUI helpers
        self.l_triangle = None
        self.r_triangle = None

        self.bar_shift = 0
        self.old_left = 0
        self.old_right = 0

    def drawWidget(self, qp):
        size = self.size()
        w = size.width()
        h = size.height()
        pt = self.padding_top
        ps = self.padding_side

        qp.setPen(QColor(100, 100, 100))
        qp.drawLine(ps, pt, w - ps, pt)
        qp.setPen(Qt.NoPen)
        qp.setBrush(self.default_color)

        lv = self.val_to_vis(self.left)
        rv = self.val_to_vis(self.right)
        if self.mouse_status == 3:
            qp.setBrush(self.highlight_color)
        else:
            qp.setBrush(self.default_color)
        qp.drawRect(lv, pt, rv - lv, self.barwidth)
        qp.setRenderHint(QPainter.Antialiasing)
        self.l_triangle, self.r_triangle = (
            self._equilateral_triangle_points((val, pt + self.barwidth))
            for val in [lv, rv]
        )

        for triangle, label in zip([self.l_triangle, self.r_triangle], [1, 2]):
            if self.mouse_status == label:
                qp.setBrush(self.highlight_color)
            else:
                qp.setBrush(self.default_color)

            qp.drawPolygon(*map(lambda point: QPointF(*point), triangle))

    def mousePressEvent(self, ev):
        self.old_left = self.left
        self.old_right = self.right
        self.mouse_start_x = ev.x()
        self.mouse_start_y = self.l_triangle[1][1]
        self.mouse_status = 0

        # check if mouse is pressed on any of the handles
        for triangle, label in zip([self.l_triangle, self.r_triangle], [1, 2]):
            if (triangle[1][0] < self.mouse_start_x < triangle[2][0]) and (
                triangle[0][1] < ev.y() < triangle[1][1]
            ):
                self.mouse_status = label

        # check if mose is pressed on the bar
        if (self.l_triangle[0][0] < self.mouse_start_x < self.r_triangle[0][0]) and (
            self.l_triangle[0][1] - self.barwidth - 2
            < ev.y()
            < self.l_triangle[0][1] + 2
        ):
            self.mouse_status = 3

        if self.mouse_status > 0:
            global_xy = self.mapToGlobal(QPoint(self.mouse_start_x, self.mouse_start_y))
            self.popup.show()
            self.popup.setGeometry(
                global_xy.x() - self.magnifier_height // 2,
                global_xy.y(),
                self.magnifier_height,
                self.magnifier_height,
            )

    def set_left_vis(self, visval):
        self.left = max(self.min_val, self.vis_to_val(visval))

    def set_right_vis(self, visval):
        self.right = max(self.max_val, self.vis_to_val(visval))

    def set_lr(self, l=None, r=None):
        if l is None:
            l = self.left
        if r is None:
            r = self.right

        if (r > l) and (l > self.min_val) and (r < self.max_val):
            self.left = l
            self.right = r

    def mouseMoveEvent(self, ev):
        x = ev.x()
        delta = x - self.mouse_start_x
        amplification = self.f_amp(abs(ev.y() - self.mouse_start_y))

        x_n = self.vis_to_val_relative(delta * amplification)
        if QApplication.instance().keyboardModifiers() == Qt.AltModifier:
            if self.mouse_status == 1:
                self.set_lr(self.old_left + x_n, self.old_right - x_n)
            elif self.mouse_status == 2:
                self.set_lr(self.old_left - x_n, self.old_right + x_n)
        if self.mouse_status == 1:
            self.set_lr(l=self.old_left + x_n)
        elif self.mouse_status == 2:
            self.set_lr(r=self.old_right + x_n)
            # if we drag the bar, move the bar
        elif self.mouse_status == 3:
            self.set_lr(self.old_left + x_n, self.old_right + x_n)

        self.update()
        self.popup.set_current_value(delta * amplification)
        self.sig_changed.emit(self.left, self.right)


if __name__ == "__main__":
    import qdarkstyle

    class TestP(Parametrized):
        def __init__(self):
            super().__init__()
            self.x = Param((1.0, 2.0), (0.0, 100.0))

    app = QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    win = QWidget()
    layout = QHBoxLayout()
    win.setLayout(layout)

    p = TestP()

    slider_1 = RangeSliderWidgetWithNumbers(p, "x")
    layout.addWidget(slider_1)
    win.show()
    app.exec_()
