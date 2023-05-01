from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PIL import Image
import urllib.request

import requests

WEATHER_API_KEY = "138813fd5d79c5ce2fd7622255fa5cd6"


class MapButton(QPushButton):
    def __init__(self, isSelected=False, parent=None):
        super().__init__()
        self.selected = isSelected

    def setSelected(self, status):
        self.selected = status

    def isSelected(self):
        return self.selected


class MapDialog(QDialog):
    def __init__(self, latitude, longitude, parent=None):
        super().__init__()

        self.setWindowTitle("Weather Map")

        self.latitude = latitude
        self.longitude = longitude

        self.label = QLabel(self)
        self.pixmap = QPixmap('Resources/Temperature_Map.png')
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

        self.label.setPixmap(self.pixmap)
        self.label.setGeometry(0, 0, 800, 600)

        self.cloudsButton.clicked.connect(self.cloudsButtonClick)
        self.precipitationButton.clicked.connect(self.precipitationClick)
        self.windSpeedButton.clicked.connect(self.windSpeedClick)
        self.temperatureButton.clicked.connect(self.temperatureClick)

    def cloudsButtonClick(self):
        self.cloudsButton.setSelected(True)
        self.manageButtonStates(self.cloudsButton)

        self.updatePixmapImage('Clouds')
        print(f"Clouds button status is now {self.cloudsButton.isSelected()}")

    def precipitationClick(self):
        self.precipitationButton.setSelected(True)
        self.manageButtonStates(self.precipitationButton)

        self.updatePixmapImage('Precipitation')
        print(f"Precipitation button status is now {self.precipitationButton.isSelected()}")

    def windSpeedClick(self):
        self.windSpeedButton.setSelected(True)
        self.manageButtonStates(self.windSpeedButton)

        self.updatePixmapImage('Wind')
        print(f"Wind speed button status is now {self.windSpeedButton.isSelected()}")

    def temperatureClick(self):
        self.temperatureButton.setSelected(True)
        self.manageButtonStates(self.temperatureButton)


        self.updatePixmapImage('Temperature')
        print(f"Temperature button status is now {self.temperatureButton.isSelected()}")

    def manageButtonStates(self, targetButton):
        targetButton.setStyleSheet("QPushButton:checked {background-color: #50500; border: 1px solid #1E1E1E;} ")
        for button in self.buttonList:
            if button != targetButton:
                button.setSelected(False)
                button.setStyleSheet("")

    def updatePixmapImage(self, choice):
        if choice == 'Temperature':
            image = None
            try:
                image = urllib.request.urlretrieve(f"https://tile.openweathermap.org/map/temp_new/{0}/{0}/"
                                                   f"{0}.png?appid={WEATHER_API_KEY}", 'Resources/Temperature_Map.png')
                print("Successfully retrieved png image")

                PILImage = Image.open('Resources/Temperature_Map.png')
                width, height = PILImage.size
                resizedImage = PILImage.resize((width * 3, height * 2), Image.ANTIALIAS)
                resizedImage.save('Resources/Temperature_Map.png', quality=95)

            except requests.exceptions.Timeout:
                print("Could not retrieve image: connection timed out")
            except requests.exceptions.HTTPError:
                print("Could not retrieve image: server response code 404/500")
            except requests.exceptions.ConnectionError:
                print("Could not retrieve image: could not connect to url")

            self.pixmap.load('Resources/Temperature_Map.png')


        elif choice == 'Clouds':
            try:
                image = urllib.request.urlretrieve(f"https://tile.openweathermap.org/map/clouds_new/{0}/{0}/"
                                                   f"{0}.png?appid={WEATHER_API_KEY}",
                                                   'Resources/Clouds_Map.png')
                print("Successfully retrieved png image")

                PILImage = Image.open('Resources/Clouds_Map.png')
                width, height = PILImage.size
                resizedImage = PILImage.resize((width * 3, height * 2), Image.ANTIALIAS)
                resizedImage.save('Resources/Clouds_Map.png', quality=95)

            except requests.exceptions.Timeout:
                print("Could not retrieve image: connection timed out")
            except requests.exceptions.HTTPError:
                print("Could not retrieve image: server response code 404/500")
            except requests.exceptions.ConnectionError:
                print("Could not retrieve image: could not connect to url")

            self.pixmap.load('Resources/Clouds_Map.png')

        elif choice == 'Precipitation':
            try:
                image = urllib.request.urlretrieve(f"https://tile.openweathermap.org/map/precipitation_new/{0}/{0}/"
                                                   f"{0}.png?appid={WEATHER_API_KEY}",
                                                   'Resources/Precipitation_Map.png')
                print("Successfully retrieved png image")
                PILImage = Image.open('Resources/Precipitation_Map.png')
                width, height = PILImage.size
                resizedImage = PILImage.resize((width * 3, height * 2), Image.ANTIALIAS)
                resizedImage.save('Resources/Precipitation_Map.png', quality=95)

            except requests.exceptions.Timeout:
                print("Could not retrieve image: connection timed out")
            except requests.exceptions.HTTPError:
                print("Could not retrieve image: server response code 404/500")
            except requests.exceptions.ConnectionError:
                print("Could not retrieve image: could not connect to url")

            self.pixmap.load('Resources/Precipitation_Map.png')


        elif choice == 'Wind':
            try:
                image = urllib.request.urlretrieve(f"https://tile.openweathermap.org/map/wind_new/{0}/{0}/"
                                                   f"{0}.png?appid={WEATHER_API_KEY}",
                                                   'Resources/Wind_Map.png')
                print("Successfully retrieved png image")

                PILImage = Image.open('Resources/Wind_Map.png')
                width, height = PILImage.size
                resizedImage = PILImage.resize((width * 3, height * 2), Image.ANTIALIAS)
                resizedImage.save('Resources/Wind_Map.png', quality=95)

            except requests.exceptions.Timeout:
                print("Could not retrieve image: connection timed out")
            except requests.exceptions.HTTPError:
                print("Could not retrieve image: server response code 404/500")
            except requests.exceptions.ConnectionError:
                print("Could not retrieve image: could not connect to url")

            self.pixmap.load('Resources/Wind_Map.png')


        self.label.setPixmap(self.pixmap)

