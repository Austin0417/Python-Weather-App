from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from MyCalendar import MyCalendar


class ForecastDialog(QDialog):
    def __init__(self, forecastData, parent=None):
        super().__init__()
        self.layout = QVBoxLayout()
        self.calendar = MyCalendar(self)
        self.layout.addWidget(self.calendar)
        self.setLayout(self.layout)
        self.forecast = forecastData
        self.currentDay = self.calendar.selectedDate()


        self.calendar.setMouseTracking(True)
        self.calendar.clicked.connect(lambda date: self.onDateSelected(date))

        self.markForecastOnCalendar()

    def markForecastOnCalendar(self):
        currentDayOfMonth = self.calendar.selectedDate().day()
        print("Forecasted days are: ")
        for i in range(1, len(self.forecast) + 1):
            print(f"{currentDayOfMonth + i}\n")
            markedDay = self.currentDay.addDays(i)
            weather = self.forecast[i - 1]['weather'][0]['main']
            format = QTextCharFormat()
            temperature = self.forecast[i - 1]['main']['temp']
            if weather == "Clouds":
                format.setBackground(QColor(125, 125, 125))
                self.calendar.setDateTextFormat(markedDay, format)
            elif weather == "Clear":
                format.setBackground(QColor(255, 215, 0))
                self.calendar.setDateTextFormat(markedDay, format)
            elif weather == "Rain":
                format.setBackground(QColor(0, 136, 255))
                self.calendar.setDateTextFormat(markedDay, format)


    def onDateSelected(self, date):
        if date.day() in range(self.currentDay.day() + 1, self.currentDay.day() + 6):
            print("Forecasted day was selected!")
            print(f"Forecast data for {self.calendar.monthShown()}/{date.day()}/{self.calendar.yearShown()}:"
                  f"\nWeather: {self.forecast[date.day() - self.currentDay.day() - 1]['weather'][0]['main']}"
                  f"\nTemperature: {self.forecast[date.day() - self.currentDay.day() - 1]['main']['temp']}")