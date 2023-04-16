from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from WeatherData import WeatherData
from GeoData import GeoData
from SavedListView import SavedListView
import requests

GEO_API_KEY = "AIzaSyBPYk--pNvMAFYkP-425u2a5QKY0lGS8Z4"
WEATHER_API_KEY = "138813fd5d79c5ce2fd7622255fa5cd6"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather App")

        #################################################################################
        ############## DATA MEMBERS #####################################################
        #################################################################################
        self.foregroundWidget = QStackedWidget()
        self.centralWidget = QWidget()
        self.layout = QFormLayout()
        self.locationInput = QLineEdit()
        self.weatherTextEdit = QTextEdit()
        self.advancedDetails = QToolButton()
        self.scroll = QScrollArea()
        self.effect = QGraphicsOpacityEffect()
        self.saveButton = QPushButton()

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

        listLabel = QLabel()
        listLabel.setText("Saved Locations")

        self.layout.addWidget(self.locationInput)
        self.layout.addWidget(self.weatherTextEdit)
        self.layout.addWidget(self.advancedDetails)
        self.layout.addWidget(self.scroll)
        self.layout.addWidget(self.saveButton)
        self.layout.addWidget(listLabel)
        self.layout.addWidget(self.listView)

        self.saveButton.setText("Save current location")
        self.saveButton.setEnabled(False)
        self.saveButton.setMaximumWidth(200)


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
        #self.weatherTextEdit.move(500, 300)
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
        self.listView.doubleClicked.connect(lambda index: self.onListDoubleClicked(index))

    def obtainGeoData(self, location):
        if location:
            geoParams = {'key': GEO_API_KEY, 'address': location}
        else:
          return None

        geoRequestData = requests.get("https://maps.googleapis.com/maps/api/geocode/json?", geoParams).json()
        self.geoData = GeoData(geoRequestData)

        if self.geoData.status == "OK":
            # latitude = geoRequestData['results'][0]['geometry']['location']['lat']
            # longitude = geoRequestData['results'][0]['geometry']['location']['lng']
            #print(geoRequestData[0]['address_components'][0])
            return self.geoData.latitude, self.geoData.longitude
        else:
            errorDialog = QMessageBox()
            errorDialog.setIcon(QMessageBox.Critical)
            errorDialog.setWindowTitle("Error")
            errorDialog.setText("Couldn't complete geocoding request (invalid location)")
            errorDialog.setStandardButtons(QMessageBox.Ok)
            errorDialog.exec()
            return None, None

    def obtainWeatherData(self, latitude, longitude, location):
        weatherParams = {'lat': latitude, 'lon': longitude, 'appid': WEATHER_API_KEY, 'units': 'imperial'}
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

    def displayWeatherInfo(self, weatherData):
        currentCondition = weatherData.getCurrentWeather()
        if currentCondition == "Thunderstorm":
            backgroundImage = QPixmap("Resources/Thunderstorm.jpg")
            self.centralWidget.setStyleSheet(f"background-image: url('Resources/Thunderstorm.jpg');")
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
            self.centralWidget.setStyleSheet(f"background-image: url({backgroundImage});")
        elif currentCondition == "Clouds":
            backgroundImage = QPixmap("Resources/Clouds.jpg")
            # self.setStyleSheet(f"background-image: url('Resources/Clouds.jpg'); background-repeat: no-repeat; background-size: cover; "
            #                                    f"height: 100%;")

        self.weatherTextEdit.clear()
        weatherInfo = weatherData.description + "\n" + str(weatherData.temperature) + "°F"
        self.weatherTextEdit.setText(weatherInfo)
        self.advancedDetails.setVisible(True)
        advancedDetailsText = QLabel()
        advancedDetailsText.setText("Humidity: " + str(weatherData.humidity) + "\n" + "Wind Speed: " + str(weatherData.windSpeed))
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
            print(f"{self.geoData.location} has been saved")
            self.savedLocations.append(self.geoData)
            self.savedListModel = SavedListView(self.savedLocations, None)
            self.listView.setModel(self.savedListModel)

        elif result == QMessageBox.Cancel:
            return

    def onListDoubleClicked(self, index):
        selectedGeoData = self.savedListModel.data(index.row(), Qt.UserRole)
        self.displayInfoOnDoubleClick(selectedGeoData.location)

    def onEnterPressed(self):
        location = self.locationInput.text()
        print("Entered location is : " + location)
        latitude, longitude = self.obtainGeoData(location)
        if not latitude or not longitude:
            return

        self.weatherData = self.obtainWeatherData(latitude, longitude, location)
        if not self.weatherData:
            return

        self.displayWeatherInfo(self.weatherData)
        self.saveButton.setEnabled(True)

    def displayInfoOnDoubleClick(self, location):
        latitude, longitude = self.obtainGeoData(location)
        weatherData = self.obtainWeatherData(latitude, longitude, location)
        self.displayWeatherInfo(weatherData)