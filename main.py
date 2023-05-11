import requests
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from MainWindow import MainWindow


API_KEY = "AIzaSyBPYk--pNvMAFYkP-425u2a5QKY0lGS8Z4"





app = QApplication(sys.argv)

app.setStyleSheet("""
QPushButton {
    background-color: #1e90ff;
    border-style: solid;
    border-width: 2px;
    border-radius: 25px;
    border-color: #1e90ff;
    font-size: 16px;
    color: #ffffff;
    padding: 5px 10px;
}
QPushButton:hover {
    background-color: #4d94ff;
    border-color: #4d94ff;
}
QPushButton:pressed {
    background-color: #0039e6;
    border-color: #0039e6;
}
MainWindow {
        background-color: #5A5A5A;
        border: 1px solid #c5c5c5;
        border-radius: 5px;
    }
QRadioButton {
    font-size: 16px;
    color: #fff;
    max-width: 200px;
    padding: 25px;
    border: 2px solid #ccc;
    border-radius: 20px;
    background-color: #222;
    spacing: 5px;
}

QRadioButton:hover {
    background-color: #333;
}

QRadioButton:checked {
    background-color: #444;
    border-color: #666;
}

QMessageBox {
color: black;
}

QWidget {
color: white;
}

""")

mainWindow = MainWindow()
mainWindow.resize(1000, 600)


mainWindow.show()
app.exec()

