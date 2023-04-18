from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class MyCalendar(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__()

    def mouseMoveEvent(self, event):
        position = event.pos()
        print(f"X: {position.x()}. Y: {position.y()}")