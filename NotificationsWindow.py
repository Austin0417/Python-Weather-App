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
        self.notificationsButton.setStyleSheet("width: 100px;")
        self.initialize()

    def initialize(self):
        self.setCentralWidget(self.centralWidget)
        self.windowLayout.addWidget(self.notificationsButton)
        self.windowLayout.addWidget(self.appearanceButton)
        self.centralWidget.setLayout(self.windowLayout)

        self.notificationsButton.clicked.connect(self.notificationsClick)


    def notificationsClick(self):
        self.notificationSettings.exec()
