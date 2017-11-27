import sys
import re
from PyQt5.QtWidgets import QFrame, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QLinearGradient, QPixmap, QPainterPath,QFontMetrics
from PyQt5.QtCore import pyqtProperty, pyqtSignal, pyqtSlot, Qt, QPoint, QRect
from .channel import PyDMChannel
from ..application import PyDMApplication
from .base import PyDMWidget

class PyDMLed(QFrame, PyDMWidget):
    
    #connected_signal = pyqtSignal()
    #disconnected_signal = pyqtSignal()
    valueChanged = pyqtSignal(int)

    def __init__(self, parent=None, init_channel=None):
        QFrame.__init__(self, parent=parent)
        PyDMWidget.__init__(self, init_channel=init_channel)
        self.value = None
        self._channels = None
        self._connected = False
        self.enum_strings = None
        self._channel = init_channel
        self._byte = ['0', '1']
        self._label = ['off', 'on']
        self._ledColor = ['red', 'green']
        self._showLabel = True
        self._squareLed = False
        self.current_label = ''
        self.default_color = 'black'
        self.current_color = self.default_color
        self.setFont(QFont('Arial', pointSize=14, weight=QFont.Bold))   # Default font
        #If this label is inside a PyDMApplication (not Designer) start it in the disconnected state.
        #app = QApplication.instance()
        #if isinstance(app, PyDMApplication):
        #    self.alarmSeverityChanged(self.ALARM_DISCONNECTED)

    def getLabelColor(self):
        stylesheet = self.styleSheet()
        stylesheet_raw = stylesheet.replace(' ', '').replace('\n', '')
        reg_ex = '((?<=^color:)|(?<=;color:)|(?<={color:)).*?((?=$)|(?=;)|(?=}))'
        try:
            color_property = re.search(reg_ex, stylesheet_raw).group(0)
        except:
            color_property = 'black'
        return color_property

    def drawLabel(self, qp, event):
        text_color = self.getLabelColor()
        text_line_width = 1
        qp.setBrush(QColor(text_color))
        qp.setPen(QPen(QColor('black'), text_line_width))
        text_width = QFontMetrics(self.font()).width(self.current_label)
        text_height = QFontMetrics(self.font()).height()
        text_pos_x = (event.rect().width()- text_width)*0.5
        text_pos_y = event.rect().center().y() + text_height*0.5
        qp_path = QPainterPath()
        qp_path.addText(text_pos_x, text_pos_y, self.font(), self.current_label);
        qp.drawPath(qp_path)

    def drawLed(self, qp, event):
        # Define shadow brush
        gradient_shadow = QLinearGradient(0, 0, 0, self.height())
        gradient_shadow.setColorAt(0.0, QColor('darkgrey'))
        gradient_shadow.setColorAt(1.0, QColor('lightgrey'))
        qp.setBrush(QBrush(gradient_shadow))
        LED_BORDER = 5
        # Draw shadow and alarm border
        if self._squareLed:
            x = 0
            y = 0
            lenx = self.width()
            leny = self.height()
            qp.drawRect(x, y, lenx, leny)
        else:
            x = self.width()*0.5
            y = self.height()*0.5
            radx = self.width()*0.5 - 1
            rady = self.height()*0.5 - 1
            qp.drawEllipse(QPoint(x, y), radx, rady)
        # Define led color brush
        qp.setPen(QPen(QColor('gray'), 2))
        gradient_led = QLinearGradient(0, 0, 0, self.height())
        gradient_led.setColorAt(0.0, QColor(self.current_color))
        gradient_led.setColorAt(1.0, QColor(255, 255, 255))
        qp.setBrush(QBrush(gradient_led))
        # Draw led
        if self._squareLed:
            x_led = LED_BORDER
            y_led = LED_BORDER
            lenx_led = self.width() - 2*x_led
            leny_led = self.height() - 2*y_led
            qp.drawRect(x_led, y_led, lenx_led, leny_led)
        else:
            radx_led = radx - LED_BORDER
            rady_led = rady - LED_BORDER
            qp.drawEllipse(QPoint(x, y), radx_led, rady_led)
        # Define shine brush
        qp.setPen(Qt.transparent)
        gradient_shine = QLinearGradient(0, 0, 0, self.height()*0.4)
        gradient_shine.setColorAt(0.0, QColor('white'))
        gradient_shine.setColorAt(1.0, Qt.transparent)
        qp.setBrush(QBrush(gradient_shine))
        # Draw shine
        if self._squareLed:
            x_shine = x_led + 5
            y_shine = y_led + 5
            lenx_shine = lenx_led - 2*(x_shine - x_led)
            leny_shine = leny_led - 2*(y_shine - y_led)
            qp.drawRoundedRect(x_shine, y_shine, lenx_shine, leny_shine, 5, 5)
        else:
            radx_shine = radx_led*0.65
            rady_shine = rady_led*0.60
            x_shine = x
            y_shine = rady_shine + LED_BORDER + 5
            qp.drawEllipse(QPoint(x_shine, y_shine), radx_shine, rady_shine)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing)
        qp.setPen(Qt.transparent)
        self.drawLed(qp, event)
        if self._showLabel:
            self.drawLabel(qp, event)
        qp.end()

    def updateCurrentLabel(self, new_value):
        try:
            byte_index = self._byte.index(str(new_value))
            self.current_label = self._label[byte_index]
            return
        except:
            pass
        try:
            self.current_label = self.enum_strings[new_value]
        except:
            self.current_label = str(new_value)

    def updateCurrentColor(self, new_value):
        try:
            byte_index = self._byte.index(str(new_value))
            self.current_color = self._ledColor[byte_index]
        except:
            self.current_color = self.default_color
    
    def refresh(self):
        self.updateCurrentColor(self.value)
        if self._showLabel:
            self.updateCurrentLabel(self.value)
        self.repaint()
    
    def value_changed(self, new_value):
        super(PyDMLed, self).value_changed(new_value)
        self.refresh()
        self.valueChanged.emit(new_value)

    def getByte(self):
        return self._byte

    def setByte(self, value):
        if value != self._byte:
            self._byte = value

    def resetByte(self):
        self._byte = ['0', '1']

    byte = pyqtProperty("QStringList", getByte, setByte, resetByte)

    def getLabel(self):
        return self._label

    def setLabel(self, value):
        if value != self._label:
            self._label = value

    def resetLabel(self):
        self._label = ['off', 'on']

    label = pyqtProperty("QStringList", getLabel, setLabel, resetLabel)

    def getLedColor(self):
        return self._ledColor

    def setLedColor(self, value):
        if value != self._ledColor:
            self._ledColor = value

    def resetLedColor(self):
        self._ledColor = ['r', 'g']

    ledColor = pyqtProperty("QStringList", getLedColor, setLedColor, resetLedColor)

    def getShowLabel(self):
        return self._showLabel

    def setShowLabel(self, value):
        if value != self._showLabel:
            self._showLabel = value

    def resetShowLabel(self):
        self._showLabel = True

    showLabel = pyqtProperty(bool, getShowLabel, setShowLabel, resetShowLabel)

    def getSquareLed(self):
        return self._squareLed

    def setSquareLed(self, value):
        if value != self._squareLed:
            self._squareLed = value
            self.repaint()

    def resetSquareLed(self):
        self._squareLed = False

    squareLed = pyqtProperty(bool, getSquareLed, setSquareLed, resetSquareLed)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PyDMLed()
    sys.exit(app.exec_())