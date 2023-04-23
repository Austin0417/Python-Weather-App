from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ForecastInfoDialog(QDialog):
    def __init__(self, forecastInformation, parent=None):
        super().__init__()
        self.layoutWidget = QHBoxLayout()
        self.info = QTextEdit()
        self.forecastInformation = forecastInformation
        self.layoutWidget.addWidget(self.info)
        self.info.setReadOnly(True)
        self.setLayout(self.layoutWidget)

        self.info.setText(f"Average Temperature: {self.forecastInformation[1]}\n"
                          f"Minimum Temperature: {self.forecastInformation[2]['temp_min']}\n"
                          f"Maximum Temperature: {self.forecastInformation[2]['temp_max']}\n"
                          f"Condition: {self.forecastInformation[0]}\n"
                          f"Pressure: {self.forecastInformation[2]['pressure']}\n"
                          f"Sea Level: {self.forecastInformation[2]['sea_level']}\n"
                          f"Humidity: {self.forecastInformation[2]['humidity']}\n"
                          f"")