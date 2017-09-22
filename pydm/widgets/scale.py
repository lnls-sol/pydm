import sys
from pydm.application import PyDMApplication
from pydm.PyQt.QtGui import QWidget, QVBoxLayout, QHBoxLayout, QPainter, QColor, QPolygon, QPen
from pydm.PyQt.QtCore import Qt, QPoint, pyqtSlot, pyqtProperty
from pydm.widgets.channel import PyDMChannel

class Scale(QWidget):

	def __init__(self, parent=None):
		super(Scale, self).__init__(parent)
		self._orientation = 'horizontal'
		self._divisions = 10
		self._painter = QPainter()
		self._pen = QPen()
		self._color = QColor('black')
		self._tick_width = 1

		self.setPen()
		self.show()

	def setPen(self):
		self._pen.setColor(self._color)
		self._pen.setWidth(self._tick_width)

	def drawScale(self):
		self._painter.setPen(self._pen)
		#self._painter.setBrush(QColor('green'))
		division_size = self.width() / self._divisions
		tick_size = self.height()
		# Draw ticks
		for i in range(self._divisions+1):
			self._painter.drawLine(i*division_size, 0, i*division_size, tick_size) # x1, y1, x2, y2

	def paintEvent(self, event):
		self._painter.begin(self)
		self._painter.setRenderHint(QPainter.Antialiasing)
		self.drawScale()
		self._painter.end()

class Bar(QWidget):

	def __init__(self, parent=None):
		super(Bar, self).__init__(parent)
		self._bar_color = 'lightgray'
		self._pointer_color = 'black'
		self._pointer_proportion = 0.05
		self.value = 0
		self.position = 0
		self._painter = QPainter()

	def setPosition(self):
		self.position = int(self.value * self.width())

	def setValue(self, proportion):
		self.value = proportion
		self.repaint()

	def drawIndicator(self):
		self.drawPointer()

	def drawPointer(self):
		self.setPosition()
		self._painter.setPen(Qt.transparent)
		self._painter.setBrush(QColor(self._pointer_color))
		pointer_width = self._pointer_proportion * self.width()
		pointer_height = self.height()
		points = [
                QPoint(self.position, 0),
                QPoint(self.position + 0.5*pointer_width, 0.5*self.height()),
                QPoint(self.position, self.height()),
                QPoint(self.position - 0.5*pointer_width, 0.5*self.height())
        ]
		self._painter.drawPolygon(QPolygon(points))

	def drawBackground(self):
		self._painter.setPen(Qt.transparent)
		self._painter.setBrush(QColor(self._bar_color))
		self._painter.drawRect(0, 0, self.width(), self.height())

	def paintEvent(self, event):
		self._painter.begin(self)
		#self._painter.rotate(-90)
		self._painter.setRenderHint(QPainter.Antialiasing)
		self.drawBackground()
		self.drawIndicator()
		self._painter.end()

class AbstractIndicator(QWidget):
	def __init__(self, parent=None):
		super(AbstractIndicator, self).__init__(parent)
		self.bar = Bar()
		self.scale = Scale()
		self._lower_limit = 0
		self._upper_limit = 10
		self.value = 5
		self.setValue(self.value)

		self.layout = QVBoxLayout()
		self.layout.addWidget(self.bar)
		self.layout.addWidget(self.scale)
		self.layout.setContentsMargins(1, 1, 1, 1)
		self.setLayout(self.layout)
		self.show()

	def update_indicator(self):
		proportion = (self.value - self._lower_limit) / (self._upper_limit - self._lower_limit)
		self.bar.setValue(proportion)

	def setValue(self, value):
		self._value = value
		self.update_indicator()
	
class PyDMScaleIndicator(AbstractIndicator):

	def __init__(self, parent=None, init_channel=None):
		super(PyDMScaleIndicator, self).__init__(parent)
		self._channel = init_channel
		self._channels = None
		self._lower_limit = -1
		self._upper_limit = 19

	@pyqtSlot(float)
	@pyqtSlot(int)
	@pyqtSlot(str)
	def receiveValue(self, new_value):
		self.value = new_value
		self.update_indicator()

	#false = disconnected, true = connected
	@pyqtSlot(bool)
	def connectionStateChanged(self, connected):
		pass

	#0 = NO_ALARM, 1 = MINOR, 2 = MAJOR, 3 = INVALID    
	@pyqtSlot(int)
	def alarmSeverityChanged(self, new_alarm_severity):
		pass

	@pyqtSlot(int)
	def precisionChanged(self, new_prec):
		pass

	@pyqtSlot(str)
	def unitsChanged(self, new_units):
		pass

	def getChannel(self):
		return str(self._channel)
    
	def setChannel(self, value):
		if self._channel != value:
			self._channel = str(value)

	def resetChannel(self):
		if self._channel is not None:
			self._channel = None
        
	channel = pyqtProperty(str, getChannel, setChannel, resetChannel)

	def channels(self):
		if self._channels is not None:
			return self._channels
		self._channels = [PyDMChannel(address=self.channel, connection_slot=self.connectionStateChanged, value_slot=self.receiveValue, severity_slot=self.alarmSeverityChanged, prec_slot=self.precisionChanged, unit_slot=self.unitsChanged)]
		return self._channels
	
if __name__ == '__main__':
	app = PyDMApplication()
	scale = PyDMScaleIndicator(init_channel='SOL3:DMC1:m3.RBV')
	scale.resize(300, 50)
	sys.exit(app.exec_())