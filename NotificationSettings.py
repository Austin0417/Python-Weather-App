from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class NotificationSettings(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.formLayout = QHBoxLayout(self)
        self.labelOne = QLabel("Notification Time: ", self)
        self.labelTwo = QLabel("minutes ", self)
        self.notificationTimerInput = QLineEdit(self)
        self.initialize()

    def initialize(self):
        self.resize(200, 250)

        validator = QIntValidator(self)

        self.notificationTimerInput.setStyleSheet("color: black;")
        self.notificationTimerInput.setPlaceholderText(f"{self.parent().parent().notificationTimer}")
        self.notificationTimerInput.setValidator(validator)


        self.labelOne.setStyleSheet("color: black;")
        self.labelTwo.setStyleSheet("color: black;")

        self.formLayout.addWidget(self.labelOne)
        self.formLayout.addWidget(self.notificationTimerInput)
        self.formLayout.addWidget(self.labelTwo)
        self.setLayout(self.formLayout)

        self.notificationTimerInput.returnPressed.connect(self.onNotificationInputEntered)


    def onNotificationInputEntered(self):
        if self.notificationTimerInput.text():
            question = QMessageBox()
            question.setIcon(QMessageBox.Question)
            question.setStyleSheet("color: black")
            question.setWindowTitle("Notifications")
            question.setText(f"Are you sure you want to set the notification timer to {self.notificationTimerInput.text()}?")
            question.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            result = question.exec()
            if result == QMessageBox.Ok:
                self.notificationTimer = int(self.notificationTimerInput.text())
                mainWindow = self.parent().parent()
                mainWindow.notificationTimer = int(self.notificationTimerInput.text())
                mainWindow.updateNotificationTime(self.notificationTimer)
            else:
                return
        else:
            return

