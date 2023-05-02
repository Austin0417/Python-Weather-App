from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from WeatherData import WeatherData
from GeoData import GeoData
from SavedListView import SavedListView
from ForecastDialog import ForecastCalendarDialog
from MapDialog import MapDialog
from plyer import notification
from apscheduler.schedulers.background import BackgroundScheduler
import re
import requests
import time
import threading
import schedule
import urllib.request
from PIL import Image

GEO_API_KEY = "AIzaSyBPYk--pNvMAFYkP-425u2a5QKY0lGS8Z4"
WEATHER_API_KEY = "138813fd5d79c5ce2fd7622255fa5cd6"
TIME_ZONE_API_KEY = "J733K9SEJOU9"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather App")

        #################################################################################
        ############## DATA MEMBERS #####################################################
        #################################################################################
        self.foregroundWidget = QStackedWidget()
        self.centralWidget = QWidget(self)
        self.layout = QFormLayout(self)
        self.locationInput = QLineEdit(self)
        self.timeLabel = QLabel()
        self.weatherTextEdit = QTextEdit(self)
        self.advancedDetails = QToolButton(self)
        self.scroll = QScrollArea(self)
        self.effect = QGraphicsOpacityEffect()
        self.saveButton = QPushButton(self)
        self.forecastButton = QPushButton()
        self.quitButton = QPushButton()
        self.mapButton = QPushButton()
        self.fahrenheitButton = QRadioButton("Fahrenheit")
        self.celsiusButton = QRadioButton("Celsius")
        self.kelvinButton = QRadioButton("Kelvin")
        self.temperatureSelection = QButtonGroup()
        self.locationWeatherMapping = {}

        self.scheduler = BackgroundScheduler()


        self.savedLocations = []
        self.listView = QListView()
        self.savedListModel = None

        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.weatherData = None
        self.geoData = None


        #################################################################################
        #################################################################################
        #################################################################################

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
        self.layout.addWidget(self.kelvinButton)
        self.layout.addWidget(self.celsiusButton)
        self.layout.addWidget(self.fahrenheitButton)
        self.layout.addWidget(self.timeLabel)
        self.layout.addWidget(self.weatherTextEdit)
        self.layout.addWidget(self.advancedDetails)
        self.layout.addWidget(self.scroll)
        self.layout.addWidget(self.saveButton)
        self.layout.addWidget(listLabel)
        self.layout.addWidget(self.listView)
        self.layout.addWidget(self.forecastButton)
        self.layout.addWidget(self.mapButton)
        self.layout.addWidget(self.quitButton)


        self.mapButton.setText("Weather Map")
        self.mapButton.setMaximumWidth(150)
        self.mapButton.setEnabled(False)

        self.listView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listView.setMaximumWidth(250)

        self.forecastButton.setText("Next 5 days forecast")
        self.forecastButton.setMaximumWidth(150)
        self.forecastButton.setEnabled(False)

        self.saveButton.setText("Save current location")
        self.saveButton.setEnabled(False)
        self.saveButton.setMaximumWidth(200)

        self.quitButton.setText("Exit")
        self.quitButton.setMaximumWidth(100)


        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.InBack)

        self.locationInput.setFont(QFont("Helvetica"))
        self.locationInput.setClearButtonEnabled(True)
        self.locationInput.addAction(QIcon("Resources/magnifying_glass_icon.png"), QLineEdit.LeadingPosition)
        self.locationInput.setPlaceholderText("Enter location (ZIP Code, City, Address)")
        self.locationInput.setStyleSheet("""
            QLineEdit {
                border-radius: 10px;
                height: 25px;
                padding: 10px;
            }
        """)

        self.scroll.setWidgetResizable(True)
        self.scroll.setVisible(False)
        self.scroll.setStyleSheet("border: none")
        self.scroll.setMaximumHeight(35)

        self.advancedDetails.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.advancedDetails.setText("Advanced Weather Info")
        self.advancedDetails.setArrowType(2)
        self.advancedDetails.setCheckable(True)
        self.advancedDetails.setVisible(False)
        self.advancedDetails.move(800, 150)

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

        self.locationInput.returnPressed.connect(self.onEnterPressed)
        self.advancedDetails.clicked.connect(self.onDropDownClick)
        self.saveButton.clicked.connect(self.onSavePressed)
        self.forecastButton.clicked.connect(self.onForecastButtonClick)
        self.listView.doubleClicked.connect(lambda index: self.onListDoubleClicked(index))
        self.listView.customContextMenuRequested.connect(lambda pos: self.onListViewRightClick(pos))
        self.temperatureSelection.buttonClicked.connect(lambda button: self.onTemperatureSelectionClick(button))
        self.quitButton.clicked.connect(self.onQuitButtonClick)
        self.mapButton.clicked.connect(self.onMapButtonClick)

        self.scheduler.add_job(self.requestConditionPeriodically, 'interval', minutes=10)
        scheduler_thread = threading.Thread(target=self.scheduler.start)
        scheduler_thread.start()

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

        if self.temperatureSelection.checkedId() == 0:
            weatherInfo = f" {weatherData.description} \n {weatherData.temperature}K"
        elif self.temperatureSelection.checkedId() == 1:
            weatherInfo = f" {weatherData.description} \n {weatherData.temperature}°C"
        else:
            weatherInfo = f" {weatherData.description} \n {weatherData.temperature}°F"

        self.weatherTextEdit.setText(weatherInfo)

        self.advancedDetails.setVisible(True)
        advancedDetailsText = QLabel()
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

    def onSavePressed(self):
        result = QMessageBox.question(self, "Save Location Confirmation", "Are you sure you want to save the currently entered location?", QMessageBox.Ok | QMessageBox.Cancel)
        if result == QMessageBox.Ok:
            for geoData in self.savedLocations:
                if self.geoData.location == geoData.location:
                    message = QMessageBox()
                    message.setIcon(QMessageBox.Critical)
                    message.setWindowTitle("Error")
                    message.setText("Current location is already saved!")
                    message.setStandardButtons(QMessageBox.Ok)
                    message.exec()
                    return
            print(f"{self.geoData.location} has been saved")
            self.savedLocations.append(self.geoData)
            self.savedListModel = SavedListView(self.savedLocations, None)
            self.listView.setModel(self.savedListModel)
            enableNotifications = QMessageBox.question(self, "Notifications",
                                                       f'Would you like to enable notifications for {self.geoData.location}?',
                                                       QMessageBox.Ok | QMessageBox.Cancel)
            if enableNotifications == QMessageBox.Ok:
                self.locationWeatherMapping[self.geoData.location] = self.weatherData.currentCondition
            else:
                return
        elif result == QMessageBox.Cancel:
            return

    def onTemperatureSelectionClick(self, button):
        button.setChecked(True)
        if self.weatherTextEdit.toPlainText():
            text = self.weatherTextEdit.toPlainText()
            previousTemperature = text.split(' ')
            previousTemperatureValue = float(re.sub('[^0-9.]', '', previousTemperature[-1]))
            print(previousTemperature)
            if 'F' in previousTemperature[-1] and self.temperatureSelection.checkedId() == 0:
                # Fahrenheit to Kelvin conversion
                print("Fahrenheit to Kelvin")
                kelvinTemp = round(float((5/9)*((previousTemperatureValue + 459.67))), 2)
                previousTemperature[-1] = str(kelvinTemp) + 'K'
                newText = ' '.join(previousTemperature)
                self.weatherTextEdit.clear()
                self.weatherTextEdit.setText(newText)
            elif 'F' in previousTemperature[-1] and self.temperatureSelection.checkedId() == 1:
                # Fahrenheit to Celsius conversion
                print("Fahrenheit to Celsius")
                celsiusTemp = round(float((5/9)*((previousTemperatureValue - 32))), 2)
                previousTemperature[-1] = str(celsiusTemp) + '°C'
                newText = ' '.join(previousTemperature)
                self.weatherTextEdit.clear()
                self.weatherTextEdit.setText(newText)
            elif 'C' in previousTemperature[-1] and self.temperatureSelection.checkedId() == 0:
                # Celsius to Kelvin conversion
                print("Celsius to Kelvin")
                kelvinTemp = round(float(previousTemperatureValue + 273.15), 2)
                previousTemperature[-1] = str(kelvinTemp) + 'K'
                newText = ' '.join(previousTemperature)
                self.weatherTextEdit.clear()
                self.weatherTextEdit.setText(newText)
            elif 'C' in previousTemperature[-1] and self.temperatureSelection.checkedId() == 2:
                # Celsius to Fahrenheit conversion
                print("Celsius to Fahrenheit")
                fahrenheitTemp = round(float((previousTemperatureValue * (9/5)) + 32), 2)
                previousTemperature[-1] = str(fahrenheitTemp) + '°F'
                newText = ' '.join(previousTemperature)
                self.weatherTextEdit.clear()
                self.weatherTextEdit.setText(newText)
            elif 'K' in previousTemperature[-1] and self.temperatureSelection.checkedId() == 1:
                # Kelvin to Celsius conversion
                print("Kelvin to Celsius")
                celsiusTemp = round(float(previousTemperatureValue - 273.15), 2)
                previousTemperature[-1] = str(celsiusTemp) + '°C'
                newText = ' '.join(previousTemperature)
                self.weatherTextEdit.clear()
                self.weatherTextEdit.setText(newText)
            elif 'K' in previousTemperature[-1] and self.temperatureSelection.checkedId() == 2:
                # Kelvin to Fahrenheit conversion
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
            self.saveButton.setText("Save " + self.geoData.location)
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
        result = QMessageBox.question(self, "Exit confirmation", "Exit weather app?", QMessageBox.Ok | QMessageBox.Cancel)
        if result == QMessageBox.Ok:
            self.close()
        else:
            return

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
                    title='Weather Notification',
                    message=f'{location} weather updated',
                    app_name='Weather App',
                    timeout=5
                )
                self.locationWeatherMapping[location] = weatherData.currentCondition
            else:
                ###############################################################################
                ############### JUST FOR TESTING, MAKE SURE TO REMOVE LATER
                ###############################################################################
                notification.notify(
                    title='Weather Notification',
                    message=f'{location} weather no updates',
                    app_name='Weather App',
                    timeout=5
                )
            time.sleep(3)




