from PyQt4.QtGui import QCheckBox, QApplication, QColor, QPalette
from PyQt4.QtCore import pyqtSignal, pyqtSlot, pyqtProperty, QState, QStateMachine, QPropertyAnimation, QString
from channel import PyDMChannel

class PyDMCheckbox(QCheckBox):
  __pyqtSignals__ = ("send_value_signal(QString)",
                     "connected_signal()",
                     "disconnected_signal()", 
                     "no_alarm_signal()", 
                     "minor_alarm_signal()", 
                     "major_alarm_signal()", 
                     "invalid_alarm_signal()")
                     
  #Emitted when the user changes the value.
  send_value_signal = pyqtSignal(QString)
  
  def __init__(self, channel=None, parent=None):
    super(PyDMCheckbox, self).__init__(parent)
    self._channel = channel
    self.clicked.connect(self.sendValue)
      
  @pyqtSlot(int)
  def receiveValue(self, new_val):
    if new_val > 0:
      self.setChecked(True)
    else:
      self.setChecked(False)
  
  @pyqtSlot(bool)
  def sendValue(self, checked):
    if checked:
      self.send_value_signal.emit(QString.number(1))
    else:
      self.send_value_signal.emit(QString.number(0))
    
  @pyqtSlot(bool)
  def connectionStateChanged(self, connected):
    self.setEnabled(connected)
  
  @pyqtSlot(bool)
  def writeAccessChanged(self, write_access):
    self.setCheckable(write_access)
  
  def getChannel(self):
    return QString.fromAscii(self._channel)
  
  def setChannel(self, value):
    if self._channel != value:
      self._channel = str(value)

  def resetChannel(self):
    if self._channel != None:
      self._channel = None
    
  channel = pyqtProperty("QString", getChannel, setChannel, resetChannel)

  def channels(self):
    return [PyDMChannel(address=self.channel, connection_slot=self.connectionStateChanged, value_slot=self.receiveValue, write_access_slot=self.writeAccessChanged, value_signal=self.send_value_signal)]