from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from NotificationSettings import NotificationSettings


class NotificationsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notificationSettings = NotificationSettings(self)
        self.centralWidget = QWidget(self)
        self.setWindowTitle("Settings")
        self.windowLayout = QVBoxLayout(self)
        self.notificationsButton = QPushButton("Notifications", self)
        self.appearanceButton = QPushButton("Appearance", self)
        self.saveButton = QPushButton("Save Settings", self)
        self.notificationsButton.setStyleSheet("width: 100px;")
        self.initialize()

    def initialize(self):
        self.setCentralWidget(self.centralWidget)
        self.windowLayout.addWidget(self.notificationsButton)
        self.windowLayout.addWidget(self.appearanceButton)
        self.windowLayout.addWidget(self.saveButton)
        self.centralWidget.setLayout(self.windowLayout)

        self.notificationsButton.clicked.connect(self.notificationsClick)
        self.saveButton.clicked.connect(self.saveButtonClick)


    def notificationsClick(self):
        self.notificationSettings.exec()

    def saveButtonClick(self):
        if not self.parent().isLoggedIn:
            message = QMessageBox()
            message.setStyleSheet("color: black;")
            message.setText("You must create an account first to save settings.")
            message.exec()
        else:
            question = QMessageBox()
            question.setStyleSheet("color: black;")
            question.setText("Save current settings (notification time, saved locations, etc.)?")
            question.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            result = question.exec()

            if result == QMessageBox.Ok:
                self.parent().accounts.execute(f"UPDATE user_settings SET setting_value = '{self.parent().notificationTimer}'"
                                               f" WHERE user_id = '{self.parent().userID}' AND setting_key = 'NOTIFICATION_TIME'")
                self.parent().accounts.commit()