from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import re


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


    def setUserSettings(self, id, notificationTimer):
        self.parent().userID = id

        self.parent().notificationTimer = notificationTimer
        self.parent().updateNotificationTime(notificationTimer)


    def fetchUserSettings(self, username, password):
        id = self.parent().accounts.execute(f"SELECT user_id FROM accounts WHERE (username='{username}' "
                                       f"OR email='{username} ')"
                                       f"AND password='{password}'").fetchone()[0]

        notificationTimer = int(self.parent().accounts.execute(f"SELECT setting_value FROM user_settings WHERE user_id = '{id}' "
                                           f"AND setting_key = 'NOTIFICATION_TIME'").fetchone()[0])

        return id, notificationTimer

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
        cursor = self.parent().accounts.execute(f"SELECT * FROM accounts WHERE (username='{self.usernameInput.text()}' OR email='{self.usernameInput.text()}')"
                                                f"AND password='{self.passwordInput.text()}'")
        if cursor.fetchone():
            print("Account found! Logging in")
            self.parent().isLoggedIn = True
            self.parent().currentUserName = self.usernameInput.text()

            id, notificationTimer = self.fetchUserSettings(self.usernameInput.text(), self.passwordInput.text())

            self.setUserSettings(id, notificationTimer)

        else:
            print("Invalid account credentials")

    def createNewAccount(self):
        if not self.passwordCreation.text() or not self.usernameCreation.text() or not self.emailCreation.text():
            return
        else:
            self.parent().accounts.execute("INSERT INTO accounts (email, username, password) VALUES (?, ?, ?)",
                                           (self.emailCreation.text(),
                                            self.usernameCreation.text(),
                                            self.passwordCreation.text()))
            self.parent().accounts.commit()

            notificationTimer = self.parent().notificationTimer
            accountsUserId = self.parent().accounts.execute(f"SELECT user_id FROM accounts WHERE username='{self.usernameCreation.text()}'").fetchone()
            print(accountsUserId[0])
            if accountsUserId:
                self.parent().accounts.execute(f"INSERT INTO user_settings (user_id, setting_key, setting_value) "
                                               f"VALUES (?, ?, ?)",
                                               (accountsUserId[0],
                                               "NOTIFICATION_TIME",
                                               str(self.parent().notificationTimer)))
                self.parent().accounts.commit()
                print("Successfully created account!")
                message = QMessageBox(self)
                message.setStyleSheet("color: black;")
                message.setText("Account creation successful!")
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
