import requests
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from MainWindow import MainWindow


API_KEY = "AIzaSyBPYk--pNvMAFYkP-425u2a5QKY0lGS8Z4"





app = QApplication(sys.argv)
mainWindow = MainWindow()
mainWindow.resize(1000, 600)
mainWindow.setStyleSheet("display: flex;")

mainWindow.show()
app.exec()

