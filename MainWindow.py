from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from WeatherData import WeatherData
from GeoData import GeoData
from SavedListView import SavedListView
from ForecastDialog import ForecastCalendarDialog
from MapDialog import MapDialog
from NotificationsWindow import NotificationsWindow
from LoginWindow import *
from plyer import notification
from apscheduler.schedulers.background import BackgroundScheduler
import json
import re
import requests
import time
import threading
import schedule
import sqlite3
import urllib.request
from PIL import Image

GEO_API_KEY = "AIzaSyBPYk--pNvMAFYkP-425u2a5QKY0lGS8Z4"
WEATHER_API_KEY = "138813fd5d79c5ce2fd7622255fa5cd6"
TIME_ZONE_API_KEY = "J733K9SEJOU9"


DEFAULT_NOTIFICATION_TIME = 30



class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Weather App")

        #################################################################################
        ############## DATA MEMBERS #####################################################
        #################################################################################
        self.foregroundWidget = QStackedWidget()
        self.centralWidget = QWidget(self)
        self.layout = QFormLayout(self)
        self.locationInput = QLineEdit(self)


        self.timeLabel = QLabel()
        self.usernameDisplay = QLabel("Guest", self)

        self.weatherTextEdit = QTextEdit(self)

        self.optionsButton = QToolButton(self)
        self.advancedDetails = QToolButton(self)

        self.scroll = QScrollArea(self)

        self.saveButton = QPushButton(self)
        self.forecastButton = QPushButton(self)
        self.quitButton = QPushButton(self)
        self.mapButton = QPushButton(self)
        self.loginButton = QPushButton(self)

        self.fahrenheitButton = QRadioButton("°F", self)
        self.celsiusButton = QRadioButton("°C", self)
        self.kelvinButton = QRadioButton('K', self)

        self.temperatureSelection = QButtonGroup(self)

        self.locationWeatherMapping = {}

        self.scheduler = BackgroundScheduler()


        self.notificationTimer = DEFAULT_NOTIFICATION_TIME
        self.notificationWindow = NotificationsWindow(self)

        self.loginWindow = LoginWindow(self)

        self.savedLocations = []
        self.listView = QListView()

        self.savedListModel = None
        self.weatherData = None
        self.geoData = None

        self.isLoggedIn = False
        self.currentUserName = None
        self.userID = None


        self.accounts = sqlite3.connect('accounts.db')



        #################################################################################
        #################################################################################
        #################################################################################
        self.accounts.execute("CREATE TABLE IF NOT EXISTS accounts (username TEXT,"
                              " password TEXT,"
                              " email TEXT,"
                              " user_id INTEGER PRIMARY KEY AUTOINCREMENT)")
        self.accounts.execute("CREATE TABLE IF NOT EXISTS user_settings "
                              "(user_id INTEGER,"
                              "setting_key TEXT,"
                              "setting_value TEXT,"
                              "FOREIGN KEY (user_id) REFERENCES accounts(user_id))")




        self.initializeUI()

    def initializeUI(self):

        self.setCentralWidget(self.centralWidget)

        self.temperatureSelection.addButton(self.kelvinButton, 0)
        self.temperatureSelection.addButton(self.celsiusButton, 1)
        self.temperatureSelection.addButton(self.fahrenheitButton, 2)
        self.fahrenheitButton.setChecked(True)

        listLabel = QLabel()
        listLabel.setText("Saved Locations")

        self.layout.addWidget(self.locationInput)
        self.layout.addWidget(self.timeLabel)
        self.layout.addWidget(self.weatherTextEdit)
        self.layout.addWidget(listLabel)
        self.layout.addWidget(self.listView)

        self.kelvinButton.move(860, 200)
        self.celsiusButton.move(860, 225)
        self.fahrenheitButton.move(860, 250)

        self.mapButton.setText("Map")
        self.mapButton.setMaximumWidth(150)
        self.mapButton.move(860, 110)
        self.mapButton.setEnabled(False)

        self.listView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listView.setStyleSheet("color: black; background-color: #d3d3d3")
        self.listView.setMaximumWidth(250)

        self.forecastButton.setText("Forecast")
        self.forecastButton.setEnabled(False)
        self.forecastButton.move(860, 70)

        self.saveButton.setText("Save")
        self.saveButton.setEnabled(False)
        #self.saveButton.setMaximumWidth(200)
        self.saveButton.move(280, 558)

        self.quitButton.setText("Exit")
        self.quitButton.setMaximumWidth(100)
        self.quitButton.move(860, 550)

        self.loginButton.move(860, 470)
        self.loginButton.setText("Login")


        self.optionsButton.move(860, 510)
        self.optionsButton.setText("Options")
        self.optionsButton.setIcon(QIcon("Resources/options_icon.png"))
        self.optionsButton.setStyleSheet("width: 75px;")


        self.usernameDisplay.setStyleSheet("color: black; font-size: 16px;")
        self.usernameDisplay.setPixmap(QPixmap("Resources/user_icon.png").scaled(25, 25))


        self.locationInput.setFont(QFont("Helvetica"))
        self.locationInput.setClearButtonEnabled(True)
        self.locationInput.addAction(QIcon("Resources/magnifying_glass_icon.png"), QLineEdit.LeadingPosition)
        self.locationInput.setPlaceholderText(f"Enter location (ZIP Code, City, Address)")
        self.locationInput.setStyleSheet("""
                border-radius: 10px;
                height: 25px;
                padding: 10px;
                background-color: #d3d3d3;
                color: black
        """)

        self.scroll.setWidgetResizable(True)
        self.scroll.setVisible(False)
        self.scroll.setStyleSheet("border: none; max-width: 215px;")
        self.scroll.move(650, 100)


        self.advancedDetails.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.advancedDetails.setText("Advanced Weather Info")
        self.advancedDetails.setArrowType(2)
        self.advancedDetails.setCheckable(True)
        self.advancedDetails.setVisible(False)
        self.advancedDetails.move(650, 70)

        self.weatherTextEdit.setStyleSheet("background-color: transparent; border: none; border: 0;")
        self.weatherTextEdit.setMaximumWidth(600)
        self.weatherTextEdit.move(500, 300)
        self.weatherTextEdit.setReadOnly(True)
        self.weatherTextEdit.setAlignment(Qt.AlignCenter)
        self.weatherTextEdit.setFontFamily("Roboto")
        self.weatherTextEdit.setFontPointSize(45.0)



        self.centralWidget.setLayout(self.layout)
        #self.setCentralWidget(self.foregroundWidget)
        self.setGeometry(100, 100, 500, 500)

        # Adding event listeners for various widgets

        self.locationInput.returnPressed.connect(self.onEnterPressed)
        self.advancedDetails.clicked.connect(self.onDropDownClick)
        self.saveButton.clicked.connect(self.onSavePressed)
        self.forecastButton.clicked.connect(self.onForecastButtonClick)
        self.listView.doubleClicked.connect(lambda index: self.onListDoubleClicked(index))
        self.listView.customContextMenuRequested.connect(lambda pos: self.onListViewRightClick(pos))
        self.temperatureSelection.buttonClicked.connect(lambda button: self.onTemperatureSelectionClick(button))
        self.quitButton.clicked.connect(self.onQuitButtonClick)
        self.optionsButton.clicked.connect(self.onOptionsButtonClick)
        self.mapButton.clicked.connect(self.onMapButtonClick)
        self.loginButton.clicked.connect(self.onLoginClick)

        self.scheduler.add_job(self.requestConditionPeriodically, 'interval', minutes=self.notificationTimer)
        scheduler_thread = threading.Thread(target=self.scheduler.start)
        scheduler_thread.start()

        print(self.accounts.execute("SELECT * FROM accounts").fetchall())
        print(self.accounts.execute("SELECT * FROM user_settings").fetchall())

    # Returns GeoData object given location, also time zone data
    def obtainGeoData(self, location):
        if location:
            geoParams = {'key': GEO_API_KEY, 'address': location}
        else:
          return None, None

        geoRequestData = requests.get("https://maps.googleapis.com/maps/api/geocode/json?", geoParams).json()


        if geoRequestData['status'] != "OK":
            #return self.geoData.latitude, self.geoData.longitude
            errorDialog = QMessageBox()
            errorDialog.setIcon(QMessageBox.Critical)
            errorDialog.setWindowTitle("Error")
            errorDialog.setText("Couldn't complete geocoding request (invalid location)")
            errorDialog.setStandardButtons(QMessageBox.Ok)
            errorDialog.exec()
            return None, None
        else:
            geoData = GeoData(geoRequestData)
            timeZoneParams = {'key': TIME_ZONE_API_KEY, 'format': 'json', 'by': 'position',
                              'lat': geoData.latitude, 'lng': geoData.longitude}
            timeZoneData = requests.get('http://api.timezonedb.com/v2.1/get-time-zone', timeZoneParams).json()
            print(timeZoneData['formatted'])
            print(f"Latitude of entered location: {geoData.latitude}\nLatitude of entered location: {geoData.longitude}")
            if timeZoneData['status'] == 'OK':
                return geoData, timeZoneData
            else:
                return geoData, None


    # Returns WeatherData object given latitude and longitude
    def obtainWeatherData(self, latitude, longitude, location):
        weatherParams = {'lat': latitude, 'lon': longitude, 'appid': WEATHER_API_KEY}
        if self.temperatureSelection.checkedId() == 1:
            weatherParams['units'] = 'metric'
        elif self.temperatureSelection.checkedId() == 2:
            weatherParams['units'] = 'imperial'
#        weatherParams = {'lat': latitude, 'lon': longitude, 'appid': WEATHER_API_KEY, 'units': 'imperial'}
        weatherRequestData = requests.get(f"https://api.openweathermap.org/data/2.5/weather?", weatherParams).json()
        weatherData = WeatherData(weatherRequestData)
        # Keys for weather json: 'coord', 'weather', 'main', 'visibility', 'wind', 'clouds', 'dt'
        print(f"Current weather conditions at {location} is: {weatherData.description}\n"
              f"Current temperature is: {weatherData.temperature} degrees Fahrenheit")

        try:
            print(f"Weather ID: {weatherData.id}")
            return weatherData
        except KeyError:
            errorDialog = QMessageBox()
            errorDialog.setIcon(QMessageBox.Critical)
            errorDialog.setWindowTitle("Error")
            errorDialog.setText("Failed to fetch weather data")
            errorDialog.setStandardButtons(QMessageBox.Ok)
            errorDialog.exec()
            return None

    # Accepts WeatherData object and time zone data as arguments to display in the GUI
    def displayWeatherInfo(self, weatherData, timeZoneData):
        time = timeZoneData['formatted'].split(' ')[1].split(':')
        hour = int(time[0])
        minute = time[1]

        convertedHour = hour % 12
        if convertedHour == 0:
            convertedHour = 12
        if hour >= 12:
            self.timeLabel.setText(f"Current weather at {self.geoData.location} as of {convertedHour}:{minute} PM: ")
        else:
            self.timeLabel.setText(f"Current weather at {self.geoData.location} as of {convertedHour}:{minute} AM: ")

        currentCondition = weatherData.getCurrentWeather()
        if currentCondition == "Thunderstorm":
            backgroundImage = QPixmap("Resources/Thunderstorm.jpg")
            self.centralWidget.setStyleSheet(f"QFormLayout{{background-image: url('Resources/Thunderstorm.jpg')}};")
        elif currentCondition == "Drizzle":
            backgroundImage = QPixmap()
            self.centralWidget.setStyleSheet(f"background-image: url({backgroundImage});")
        elif currentCondition == "Rain":
            backgroundImage = QPixmap("Resources/Rain.jpg")
            self.centralWidget.setStyleSheet(f"background-image: url({backgroundImage});")
        elif currentCondition == "Mist":
            backgroundImage = QPixmap()
            self.centralWidget.setStyleSheet(f"background-image: url({backgroundImage});")
        elif currentCondition == "Snow":
            backgroundImage = QPixmap("Resources/Snow.jpg")
            self.centralWidget.setStyleSheet(f"background-image: url({backgroundImage});")
        elif currentCondition == "Fog":
            backgroundImage = QPixmap()
            self.centralWidget.setStyleSheet(f"background-image: url({backgroundImage});")
        elif currentCondition == "Clear":
            backgroundImage = QPixmap("Resources/Clear.jpg")
            self.centralWidget.setStyleSheet(f"QFormLayout{{background-image: url({backgroundImage})}};")
        elif currentCondition == "Clouds":
            backgroundImage = QPixmap("Resources/Clouds.jpg")
            # self.setStyleSheet(f"background-image: url('Resources/Clouds.jpg'); background-repeat: no-repeat; background-size: cover; "
            #                                    f"height: 100%;")

        self.weatherTextEdit.clear()
        weatherInfo = ''

        # If the currently selected temperature format is Kelvin
        if self.temperatureSelection.checkedId() == 0:
            weatherInfo = f" {weatherData.description} \n {weatherData.temperature}K"

        # If currently selected temperature format is Celsius
        elif self.temperatureSelection.checkedId() == 1:
            weatherInfo = f" {weatherData.description} \n {weatherData.temperature}°C"

        # If currently selected temperature format is Fahrenheit
        else:
            weatherInfo = f" {weatherData.description} \n {weatherData.temperature}°F"

        # Display the updated weather information
        self.weatherTextEdit.setText(weatherInfo)

        self.advancedDetails.setVisible(True)
        advancedDetailsText = QLabel()
        advancedDetailsText.setStyleSheet("background-color: #d3d3d3; color: black; max-width: 215px;")
        advancedDetailsText.setText(f"Maximum Temperature: {weatherData.maxTemp} °F\n"
                                    f"Minimum Temperature: {weatherData.minTemp} °F\n"
                                    f"Humidity: {str(weatherData.humidity)}%\n"
                                    f"Wind Speed: {str(weatherData.windSpeed)} miles/hr\n"
                                    f"Pressure: {str(weatherData.pressure)} hPa\n"
                                    )
        self.scroll.setWidget(advancedDetailsText)


    def onDropDownClick(self):
        self.scroll.setVisible(not self.scroll.isVisible())

        if self.scroll.isVisible():
            self.advancedDetails.setArrowType(1)
        else:
            self.advancedDetails.setArrowType(2)

    def updateSavedListView(self, newLocations):
        self.savedLocations = newLocations
        self.savedListModel = SavedListView(self.savedLocations)
        self.listView.setModel(self.savedListModel)

    def onSavePressed(self):
        result = QMessageBox()
        result.setStyleSheet("color: black")
        result.setIcon(QMessageBox.Question)
        result.setWindowTitle("Save Location Confirmation")
        result.setText(f"Are you sure you want to save the currently entered location ({self.geoData.location})?")
        result.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        response = result.exec()
        #result = QMessageBox.question(self, "Save Location Confirmation", "Are you sure you want to save the currently entered location?", QMessageBox.Ok | QMessageBox.Cancel)
        if response == QMessageBox.Ok:
            for geoData in self.savedLocations:
                if self.geoData.location == geoData.location:
                    message = QMessageBox()
                    message.setStyleSheet("color: black")
                    message.setIcon(QMessageBox.Critical)
                    message.setWindowTitle("Error")
                    message.setText("Current location is already saved!")
                    message.setStandardButtons(QMessageBox.Ok)
                    message.exec()
                    return
            print(f"{self.geoData.location} has been saved")
            self.savedLocations.append(self.geoData)
            self.updateSavedListView(self.savedLocations)

            if self.isLoggedIn:
                locations = json.dumps([serializeGeoData(geodata) for geodata in self.savedLocations])
                self.accounts.execute(f"UPDATE user_settings SET setting_value='{locations}' "
                                      f"WHERE setting_key='SAVED_LOCATIONS' AND user_id='{self.userID}'")
                self.accounts.commit()


            enableNotifications = QMessageBox()
            enableNotifications.setIcon(QMessageBox.Question)
            enableNotifications.setStyleSheet("color: black")
            enableNotifications.setWindowTitle("Notifications")
            enableNotifications.setText(f"Would you like to enable notifications for {self.geoData.location}?")
            enableNotifications.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            notificationsResponse = enableNotifications.exec()
            #enableNotifications = QMessageBox.question(self, "Notifications",
                                                       #f'Would you like to enable notifications for {self.geoData.location}?',
                                                       #QMessageBox.Ok | QMessageBox.Cancel)

            if notificationsResponse == QMessageBox.Ok:
                self.locationWeatherMapping[self.geoData.location] = self.weatherData.currentCondition
            else:
                return
        elif response == QMessageBox.Cancel:
            return

    def onTemperatureSelectionClick(self, button):
        button.setChecked(True)
        if self.weatherTextEdit.toPlainText():
            text = self.weatherTextEdit.toPlainText()
            previousTemperature = text.split(' ')
            previousTemperatureValue = float(re.sub('[^0-9.]', '', previousTemperature[-1]))
            print(previousTemperature)

            # Fahrenheit to Kelvin conversion
            if 'F' in previousTemperature[-1] and self.temperatureSelection.checkedId() == 0:
                print("Fahrenheit to Kelvin")
                kelvinTemp = round(float((5/9)*((previousTemperatureValue + 459.67))), 2)
                previousTemperature[-1] = str(kelvinTemp) + 'K'
                newText = ' '.join(previousTemperature)
                self.weatherTextEdit.clear()
                self.weatherTextEdit.setText(newText)

            # Fahrenheit to Celsius conversion
            elif 'F' in previousTemperature[-1] and self.temperatureSelection.checkedId() == 1:
                print("Fahrenheit to Celsius")
                celsiusTemp = round(float((5/9)*((previousTemperatureValue - 32))), 2)
                previousTemperature[-1] = str(celsiusTemp) + '°C'
                newText = ' '.join(previousTemperature)
                self.weatherTextEdit.clear()
                self.weatherTextEdit.setText(newText)

            # Celsius to Kelvin conversion
            elif 'C' in previousTemperature[-1] and self.temperatureSelection.checkedId() == 0:
                print("Celsius to Kelvin")
                kelvinTemp = round(float(previousTemperatureValue + 273.15), 2)
                previousTemperature[-1] = str(kelvinTemp) + 'K'
                newText = ' '.join(previousTemperature)
                self.weatherTextEdit.clear()
                self.weatherTextEdit.setText(newText)

            # Celsius to Fahrenheit conversion
            elif 'C' in previousTemperature[-1] and self.temperatureSelection.checkedId() == 2:
                print("Celsius to Fahrenheit")
                fahrenheitTemp = round(float((previousTemperatureValue * (9/5)) + 32), 2)
                previousTemperature[-1] = str(fahrenheitTemp) + '°F'
                newText = ' '.join(previousTemperature)
                self.weatherTextEdit.clear()
                self.weatherTextEdit.setText(newText)

            # Kelvin to Celsius conversion
            elif 'K' in previousTemperature[-1] and self.temperatureSelection.checkedId() == 1:
                print("Kelvin to Celsius")
                celsiusTemp = round(float(previousTemperatureValue - 273.15), 2)
                previousTemperature[-1] = str(celsiusTemp) + '°C'
                newText = ' '.join(previousTemperature)
                self.weatherTextEdit.clear()
                self.weatherTextEdit.setText(newText)

            # Kelvin to Fahrenheit conversion
            elif 'K' in previousTemperature[-1] and self.temperatureSelection.checkedId() == 2:
                print("Kevlin to Fahrenheit")
                fahrenheitTemp = round(float((previousTemperatureValue - 273.15) * (9/5) + 32), 2)
                previousTemperature[-1] = str(fahrenheitTemp) + '°F'
                newText = ' '.join(previousTemperature)
                self.weatherTextEdit.clear()
                self.weatherTextEdit.setText(newText)


    def onForecastButtonClick(self):
        forecastParams = {'lat': self.geoData.latitude, 'lon': self.geoData.longitude, 'appid': WEATHER_API_KEY,
                          'units': 'imperial', 'cnt': 5}
        forecastData = requests.get("https://api.openweathermap.org/data/2.5/forecast?", forecastParams).json()

        forecastDialog = ForecastCalendarDialog(forecastData['list'], self.geoData.location, self)
        forecastDialog.exec()

    def onListDoubleClicked(self, index):
        selectedGeoData = self.savedListModel.data(index.row(), Qt.UserRole)
        self.displayInfoOnDoubleClick(selectedGeoData.location)

    def onEnterPressed(self):
        location = self.locationInput.text()
        if location:
            print("Entered location is : " + location)

            self.geoData, timeZoneData = self.obtainGeoData(location)
            if not self.geoData or not timeZoneData:
                return

            self.weatherData = self.obtainWeatherData(self.geoData.latitude, self.geoData.longitude, location)
            if not self.weatherData:
                return

            self.displayWeatherInfo(self.weatherData, timeZoneData)
            self.saveButton.setEnabled(True)
            # self.saveButton.setText("Save " + self.geoData.location)
            self.forecastButton.setEnabled(True)
            self.mapButton.setEnabled(True)
        else:
            errorDialog = QMessageBox()
            errorDialog.setIcon(QMessageBox.Critical)
            errorDialog.setWindowTitle("Error")
            errorDialog.setText("Location field is empty!")
            errorDialog.setStandardButtons(QMessageBox.Ok)
            errorDialog.exec()

    def displayInfoOnDoubleClick(self, location):
        self.geoData, timeZoneData = self.obtainGeoData(location)
        self.weatherData = self.obtainWeatherData(self.geoData.latitude, self.geoData.longitude, location)
        self.displayWeatherInfo(self.weatherData, timeZoneData)
        self.locationInput.setText(self.geoData.location)

    def onListViewRightClick(self, pos):
        index = self.listView.indexAt(pos)
        if (index.isValid()):
            locationGeoData = self.savedListModel.data(index.row(), Qt.UserRole)
            customMenu = QMenu()
            customMenu.setStyleSheet("color: black")
            viewAction = QAction("View weather")
            removeAction = QAction("Remove")
            notifications = None
            if locationGeoData.location in self.locationWeatherMapping:
                notifications = QAction('Notifications on')
                notifications.setIcon(QIcon('Resources/checkmark.png'))
            else:
                notifications = QAction('Enable notifications')

            removeAction.triggered.connect(self.onRemoveActionRightClick)
            viewAction.triggered.connect(self.onViewActionRightClick)
            notifications.triggered.connect(self.notificationsRightClick)

            customMenu.addAction(viewAction)
            customMenu.addAction(removeAction)
            customMenu.addAction(notifications)
            customMenu.exec(self.listView.viewport().mapToGlobal(pos))

    def onRemoveActionRightClick(self):
        index = self.listView.currentIndex()
        if (index.isValid()):
            selectedGeoData = self.savedListModel.data(index.row(), Qt.UserRole)
            for i in range(len(self.savedLocations)):
                if self.savedLocations[i].location == selectedGeoData.location:
                    self.savedLocations.pop(i)
            if selectedGeoData.location in self.locationWeatherMapping:
                del self.locationWeatherMapping[selectedGeoData.location]
            self.savedListModel = SavedListView(self.savedLocations, None)
            self.listView.setModel(self.savedListModel)


    def onViewActionRightClick(self):
        index = self.listView.currentIndex()
        if index.isValid():
            selectedGeoData = self.savedListModel.data(index.row(), Qt.UserRole)
            timeZoneParams = {'key': TIME_ZONE_API_KEY, 'format': 'json', 'by': 'position',
                              'lat': selectedGeoData.latitude, 'lng': selectedGeoData.longitude}
            timeZoneData = requests.get('http://api.timezonedb.com/v2.1/get-time-zone', timeZoneParams).json()
            if timeZoneData['status'] == "OK":
                weatherData = self.obtainWeatherData(selectedGeoData.latitude, selectedGeoData.longitude, selectedGeoData.location)
                self.displayWeatherInfo(weatherData, timeZoneData)
                self.locationInput.setText(selectedGeoData.location)
            else:
                raise Exception("Could not obtain time data!")

    def notificationsRightClick(self):
        index = self.listView.currentIndex()
        if index.isValid():
            selectedGeoData = self.savedListModel.data(index.row(), Qt.UserRole)
            if selectedGeoData.location not in self.locationWeatherMapping:
                weatherData = self.obtainWeatherData(selectedGeoData.latitude, selectedGeoData.longitude, selectedGeoData.location)
                self.locationWeatherMapping[selectedGeoData.location] = weatherData.currentCondition
            else:
                print(f"Removing notifications for {selectedGeoData.location}...")
                del self.locationWeatherMapping[selectedGeoData.location]


    def onQuitButtonClick(self):
        result = QMessageBox()
        result.setStyleSheet("color: black")
        result.setIcon(QMessageBox.Question)
        result.setText("Exit weather app?")
        result.setWindowTitle("Exit confirmation")
        result.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        response = result.exec()
        if response == QMessageBox.Ok:
            self.close()
        else:
            return

    def onOptionsButtonClick(self):
        print(f"Current notification time is {self.notificationTimer}")
        self.notificationWindow.resize(400, 500)
        self.notificationWindow.show()
        # optionsMenu = QMenu()
        # editNotificationsAction = QAction("Notification Settings")
        # optionsMenu.addAction(editNotificationsAction)
        # editNotificationsAction.triggered.connect(self.editNotifications)
        #
        # self.optionsButton.setMenu(optionsMenu)



    def editNotifications(self):
        notificationWindow = NotificationsWindow(self)
        notificationWindow.show()

    def onMapButtonClick(self):
        image = None
        try:
            image = urllib.request.urlretrieve(f"https://tile.openweathermap.org/map/temp_new/{0}/{0}/"
                                               f"{0}.png?appid={WEATHER_API_KEY}",
                                               'Resources/Temperature_Map.png')
            print("Successfully retrieved png image")

            PILImage = Image.open('Resources/Temperature_Map.png')
            width, height = PILImage.size
            resizedImage = PILImage.resize((width * 3, height * 2), Image.ANTIALIAS)
            resizedImage.save('Resources/Temperature_Map.png')

        except requests.exceptions.Timeout:
            print("Could not retrieve image: connection timed out")
        except requests.exceptions.HTTPError:
            print("Could not retrieve image: server response code 404/500")
        except requests.exceptions.ConnectionError:
            print("Could not retrieve image: could not connect to url")

        mapDialog = MapDialog(self.geoData.latitude, self.geoData.longitude)
        mapDialog.exec()

    def onLoginClick(self):
        if not self.isLoggedIn:
            self.loginWindow.show()
        else:
            result = QMessageBox()
            result.setStyleSheet("color: black")
            result.setIcon(QMessageBox.Question)
            result.setText("Log out?")
            result.setWindowTitle("Log out")
            result.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            response = result.exec()
            if response == QMessageBox.Ok:
                # Log the user out of their account
                self.resetMainWindow()

    def resetMainWindow(self):
        self.isLoggedIn = False
        self.currentUserName = None
        self.loginButton.setText("Login")
        self.updateSavedListView([])
        self.updateNotificationTime(DEFAULT_NOTIFICATION_TIME)


    def requestConditionPeriodically(self):
        if not self.locationWeatherMapping:
            return
        for location in self.locationWeatherMapping:
            geoData, timeZoneData = self.obtainGeoData(location)
            print(f"{geoData.latitude, geoData.longitude}\n"
                  f"{timeZoneData}")
            if not geoData or not timeZoneData:
                raise Exception("Could not process geo/time data!")
            weatherData = self.obtainWeatherData(geoData.latitude, geoData.longitude, location)
            if weatherData.currentCondition != self.locationWeatherMapping[location]:
                notification.notify(
                    title=f'{location}',
                    message=f'{weatherData.currentCondition}',
                    app_name='Weather App',
                    timeout=5
                )
                self.locationWeatherMapping[location] = weatherData.currentCondition
            else:
                notification.notify(
                    title=f'{location}',
                    message=f'No updates',
                    app_name='Weather App',
                    timeout=5
                )
            time.sleep(3)

    def updateNotificationTime(self, newNotificationTime):
        self.notificationTimer = newNotificationTime
        self.scheduler.remove_all_jobs()
        self.scheduler.add_job(self.requestConditionPeriodically, 'interval',
                                     minutes=newNotificationTime)






