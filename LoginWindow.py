from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from GeoData import GeoData
import json
import re

def serializeGeoData(obj):
    if isinstance(obj, GeoData):
        return {
            'location': obj.location,
            'latitude': obj.latitude,
            'longitude': obj.longitude
        }
    raise TypeError(f"Object of type '{type(obj).__name__}' is not JSON serializable")


class LoginWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.widgets = QStackedWidget(self)
        self.centralWidgetLogin = QWidget(self)
        self.centralWidgetAccountCreation = QWidget(self)
        self.gridLayoutLogin = QGridLayout(self)
        self.gridLayoutAccountCreation = QGridLayout(self)
        self.usernameInput = QLineEdit(self)
        self.passwordInput = QLineEdit(self)
        self.emailCreation = QLineEdit(self)
        self.usernameCreation = QLineEdit(self)
        self.passwordCreation = QLineEdit(self)

        self.invalidEmailLabel = QLabel("Invalid email address", self)
        self.createAccount = QLabel("Or create an account", self)

        self.backButton = QPushButton()

        self.initialize()

    def initialize(self):
        self.setWindowTitle("Login")

        # self.setCentralWidget(self.centralWidgetLogin)

        usernameLabel = QLabel("Username or Email: ", self)
        usernameLabel.setStyleSheet("color: black;")
        self.gridLayoutLogin.addWidget(usernameLabel)

        self.usernameInput.setStyleSheet("color: black;")
        self.gridLayoutLogin.addWidget(self.usernameInput)

        passwordLabel = QLabel("Password: ", self)
        passwordLabel.setStyleSheet("color: black;")
        self.gridLayoutLogin.addWidget(passwordLabel)

        self.passwordInput.setStyleSheet("color: black;")
        self.passwordInput.setEchoMode(QLineEdit.Password)
        self.gridLayoutLogin.addWidget(self.passwordInput)



        self.createAccount.setStyleSheet("color: blue; text-decoration: underline;")
        self.createAccount.setOpenExternalLinks(False)
        self.createAccount.setCursor(QCursor(Qt.PointingHandCursor))
        self.createAccount.mousePressEvent = self.onCreateAccountClick
        self.gridLayoutLogin.addWidget(self.createAccount)

        self.usernameInput.returnPressed.connect(self.login)
        self.passwordInput.returnPressed.connect(self.login)


        self.centralWidgetLogin.setLayout(self.gridLayoutLogin)

        ######################################################################################
        # Initializing the account creation layout in case the user needs to create an account
        ######################################################################################

        email = QLabel("Email: ")
        createUsername = QLabel("Create username: ")
        createPassword = QLabel("Create password: ")
        email.setStyleSheet("color: black;")
        createUsername.setStyleSheet("color: black;")
        createPassword.setStyleSheet("color: black;")
        self.backButton.setText("Back")

        self.invalidEmailLabel.setStyleSheet("color: red; font-weight: bold;")
        self.invalidEmailLabel.setVisible(False)
        self.usernameCreation.setStyleSheet("color: black;")
        self.passwordCreation.setStyleSheet("color: black;")
        self.passwordCreation.setEchoMode(QLineEdit.Password)
        self.emailCreation.setStyleSheet("color: black;")

        self.gridLayoutAccountCreation.addWidget(email)
        self.gridLayoutAccountCreation.addWidget(self.emailCreation)
        self.gridLayoutAccountCreation.addWidget(self.invalidEmailLabel)
        self.gridLayoutAccountCreation.addWidget(createUsername)
        self.gridLayoutAccountCreation.addWidget(self.usernameCreation)
        self.gridLayoutAccountCreation.addWidget(createPassword)
        self.gridLayoutAccountCreation.addWidget(self.passwordCreation)
        self.gridLayoutAccountCreation.addWidget(self.backButton)

        self.backButton.clicked.connect(self.onBackClicked)

        self.centralWidgetAccountCreation.setLayout(self.gridLayoutAccountCreation)

        self.widgets.addWidget(self.centralWidgetLogin)
        self.widgets.addWidget(self.centralWidgetAccountCreation)
        
        self.setCentralWidget(self.widgets)
        self.widgets.setCurrentWidget(self.centralWidgetLogin)


        self.emailCreation.returnPressed.connect(self.createNewAccount)
        self.usernameCreation.returnPressed.connect(self.createNewAccount)
        self.passwordCreation.returnPressed.connect(self.createNewAccount)

        self.emailCreation.editingFinished.connect(self.checkValidEmailInput)


    def onCreateAccountClick(self, event):
        print("Creating account...")
        self.setWindowTitle("Create Account")
        self.usernameCreation.clear()
        self.emailCreation.clear()
        self.passwordCreation.clear()
        self.invalidEmailLabel.setVisible(False)
        self.widgets.setCurrentWidget(self.centralWidgetAccountCreation)


    def setUserSettings(self, window,id, notificationTimer, locations, notificationsList):
        window.userID = id
        window.notificationTimer = notificationTimer
        window.locationWeatherMapping = notificationsList
        window.updateNotificationTime(notificationTimer)
        window.updateSavedListView(locations)



    def fetchUserSettings(self, window, username, password):
        id = window.accounts.execute(f"SELECT user_id FROM accounts WHERE (username='{username}' "
                                       f"OR email='{username} ')"
                                       f"AND password='{password}'").fetchone()[0]

        notificationTimer = int(window.accounts.execute(f"SELECT setting_value FROM user_settings WHERE user_id = '{id}' "
                                           f"AND setting_key = 'NOTIFICATION_TIME'").fetchone()[0])
        savedLocations = json.loads(window.accounts.execute(f"SELECT setting_value FROM user_settings WHERE user_id='{id}' "
                                                 f"AND setting_key='SAVED_LOCATIONS'").fetchone()[0])

        notificationsList = json.loads(window.accounts.execute(f"SELECT setting_value FROM user_settings where user_id='{id}' "
                                                               f"AND setting_key='NOTIFICATION_LIST'").fetchone()[0])

        # Convert the json of savedLocations into list of GeoData objects userLocations
        userLocations = [GeoData(None, data['location'], data['latitude'], data['longitude']) for data in savedLocations]

        return id, notificationTimer, userLocations, notificationsList

    def login(self):
        if not self.usernameInput.text() or not self.passwordInput.text():
            errorDialog = QMessageBox()
            errorDialog.setStyleSheet("color: black;")
            errorDialog.setIcon(QMessageBox.Critical)
            errorDialog.setWindowTitle("Error")
            errorDialog.setText("One or more fields empty!")
            errorDialog.setStandardButtons(QMessageBox.Ok)
            errorDialog.exec()
            return
        mainWindow = self.parent()
        cursor = mainWindow.accounts.execute(f"SELECT * FROM accounts WHERE (username='{self.usernameInput.text()}' OR email='{self.usernameInput.text()}')"
                                                f"AND password='{self.passwordInput.text()}'")
        if cursor.fetchone():
            print("Account found! Logging in")
            self.updateMainWindow(mainWindow)

            id, notificationTimer, savedLocations, notificationsList = self.fetchUserSettings(mainWindow, self.usernameInput.text(), self.passwordInput.text())

            self.setUserSettings(mainWindow, id, notificationTimer, savedLocations, notificationsList)
            message = QMessageBox()
            message.setStyleSheet("color: black;")
            message.setText("Successfully logged in!")
            message.exec()
            self.close()

        else:
            invalid = QMessageBox()
            invalid.setIcon(QMessageBox.Critical)
            invalid.setStyleSheet("color: black;")
            invalid.setText("Invalid credentials! Please try again.")
            invalid.exec()

    def createNewAccount(self):
        if not self.passwordCreation.text() or not self.usernameCreation.text() or not self.emailCreation.text():
            return
        else:
            mainWindow = self.parent()
            mainWindow.accounts.execute("INSERT INTO accounts (email, username, password) VALUES (?, ?, ?)",
                                           (self.emailCreation.text(),
                                            self.usernameCreation.text(),
                                            self.passwordCreation.text()))
            mainWindow.accounts.commit()

            notificationTimer = mainWindow.notificationTimer
            accountsUserId = mainWindow.accounts.execute(f"SELECT user_id FROM accounts WHERE username='{self.usernameCreation.text()}'").fetchone()
            print(accountsUserId[0])
            if accountsUserId:
                mainWindow.accounts.execute(f"INSERT INTO user_settings (user_id, setting_key, setting_value) "
                                               f"VALUES (?, ?, ?)",
                                               (accountsUserId[0],
                                               "NOTIFICATION_TIME",
                                               str(notificationTimer)))
                savedLocations = [serializeGeoData(geodata) for geodata in mainWindow.savedLocations]
                jsonLocations = json.dumps(savedLocations)
                mainWindow.accounts.execute(f"INSERT INTO user_settings (user_id, setting_key, setting_value) "
                                            f"VALUES (?, ?, ?)",
                                            (accountsUserId[0],
                                             "SAVED_LOCATIONS",
                                             jsonLocations))
                mainWindow.accounts.execute(f"INSERT INTO user_settings (user_id, setting_key, setting_value) VALUES (?, ?, ?)",
                                            (accountsUserId[0], "NOTIFICATION_LIST", json.dumps(mainWindow.locationWeatherMapping)))
                mainWindow.accounts.commit()
                print("Successfully created account!")
                message = QMessageBox(self)
                message.setStyleSheet("color: black;")
                message.setText("Account creation successful!")
                print(jsonLocations)
                message.exec()
            else:
                print("Couldn't create account!")
            self.widgets.setCurrentWidget(self.centralWidgetLogin)

    def onBackClicked(self):
        self.widgets.setCurrentWidget(self.centralWidgetLogin)
        self.usernameInput.clear()
        self.passwordInput.clear()

    def checkValidEmailInput(self):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not self.emailCreation.text():
            self.invalidEmailLabel.setVisible(False)
        elif not re.match(pattern, self.emailCreation.text()):
            self.invalidEmailLabel.setVisible(True)
        else:
            self.invalidEmailLabel.setVisible(False)

    def show(self):
        super().show()
        self.usernameInput.clear()
        self.passwordInput.clear()
        self.widgets.setCurrentWidget(self.centralWidgetLogin)

    def updateMainWindow(self, window):
        window.isLoggedIn = True
        window.currentUserName = self.usernameInput.text()
        window.loginButton.setText("Logout")