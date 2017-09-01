from pydm.widgets.label import PyDMLabel
from PyQt5.QtCore import pyqtProperty

class PyDMLabelDerived(PyDMLabel):
	def __init__(self, parent=None, init_channel=None):
		super(PyDMLabelDerived, self).__init__(parent, init_channel)
		self._thatProperty = 'Some text'
		self.setText('DerivedPyDMLabel')

	def getThatProperty(self):
		return str(self._thatProperty)

	def setThatProperty(self, value):
		if self._thatProperty != value:
			self._thatProperty = str(value)
        
	thatProperty = pyqtProperty(str, getThatProperty, setThatProperty)