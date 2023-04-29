from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class MapButton(QPushButton):
    def __init__(self, isSelected=False, parent=None):
        super().__init__()
        self.selected = isSelected

    def setSelected(self, status):
        self.selected = status

    def isSelected(self):
        return self.selected


class MapDialog(QDialog):
    def __init__(self, mapImage, parent=None):
        super().__init__()
        self.label = QLabel(self)
        self.pixmap = QPixmap()
        self.cloudsButton = MapButton()
        self.precipitationButton = MapButton()
        self.windSpeedButton = MapButton()
        self.temperatureButton = MapButton()
        self.mapLayout = QVBoxLayout(self)

        self.buttonList = []
        self.buttonList.append(self.cloudsButton)
        self.buttonList.append(self.precipitationButton)
        self.buttonList.append(self.windSpeedButton)
        self.buttonList.append(self.temperatureButton)

        self.pixmap.loadFromData(mapImage.content)

        self.initializeUi()

    def initializeUi(self):
        self.mapLayout.addWidget(self.label)
        self.mapLayout.addWidget(self.cloudsButton)
        self.mapLayout.addWidget(self.precipitationButton)
        self.mapLayout.addWidget(self.windSpeedButton)
        self.mapLayout.addWidget(self.temperatureButton)

        self.cloudsButton.setText("Clouds")
        self.precipitationButton.setText("Precipitation")
        self.windSpeedButton.setText("Wind Speed")
        self.temperatureButton.setText("Temperature")

        self.cloudsButton.setMaximumWidth(70)
        self.precipitationButton.setMaximumWidth(70)
        self.windSpeedButton.setMaximumWidth(70)
        self.temperatureButton.setMaximumWidth(70)

        self.label.setPixmap(self.pixmap.scaled(1000, 750))
        self.label.setGeometry(0, 0, 800, 600)

        self.cloudsButton.clicked.connect(self.cloudsButtonClick)
        self.precipitationButton.clicked.connect(self.precipitationClick)
        self.windSpeedButton.clicked.connect(self.windSpeedClick)
        self.temperatureButton.clicked.connect(self.temperatureClick)

    def cloudsButtonClick(self):
        self.cloudsButton.setSelected(True)
        self.manageButtonStates(self.cloudsButton)

        print(f"Clouds button status is now {self.cloudsButton.isSelected()}")

    def precipitationClick(self):
        self.precipitationButton.setSelected(True)
        self.manageButtonStates(self.cloudsButton)

        print(f"Precipitation button status is now {self.precipitationButton.isSelected()}")

    def windSpeedClick(self):
        self.windSpeedButton.setSelected(True)
        self.manageButtonStates(self.cloudsButton)

        print(f"Wind speed button status is now {self.windSpeedButton.isSelected()}")

    def temperatureClick(self):
        self.temperatureButton.setSelected(True)
        self.manageButtonStates(self.cloudsButton)
        print(f"Temperature button status is now {self.temperatureButton.isSelected()}")

    def manageButtonStates(self, targetButton):
        for button in self.buttonList:
            if button != targetButton:
                button.setSelected(False)
