from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from MyCalendar import MyCalendar
from ForecastInfoDialog import ForecastInfoDialog


class ForecastCalendarDialog(QDialog):
    cellEntered = pyqtSignal(object, object)

    def __init__(self, forecastData, location, parent=None):
        super().__init__()
        self.layout = QVBoxLayout()
        self.calendar = MyCalendar(self)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.setFixedSize(1000, 750)
        self.table = self.calendar.findChild(QTableView)
        self.layout.addWidget(self.calendar)
        self.setLayout(self.layout)
        self.forecast = forecastData
        self.currentDay = self.calendar.selectedDate()
        self.forecastedDayMapping = {}
        self.index = None
        self.setWindowTitle(f"Forecast for {location}")


        self.calendar.setStyleSheet("color: black")
        self.setModal(False)
        self.table.setMouseTracking(True)
        self.table.installEventFilter(self)
        self.calendar.clicked.connect(lambda date: self.onDateSelected(date))
        self.cellEntered.connect(self.handleCellEntered)

        self.markForecastOnCalendar()

    def mouseMoveEvent(self, event):
        position = event.pos()
        print("Mouse moved")
        #print(f"X: {self.mapFromGlobal(QCursor.pos()).x()}. Y: {self.mapFromGlobal(QCursor.pos()).y()}")


    def eventFilter(self, source, event):
        if source is self.table:
            if event.type() == QEvent.MouseMove:
                index = QPersistentModelIndex(source.indexAt(event.pos()))
                if index != self.index:
                    self.index = index
                    dayOfMonth = self.index.data()
                    if dayOfMonth in self.forecastedDayMapping:
                        self.cellEntered.emit(QModelIndex(index),
                                              self.mapToGlobal(QPoint(self.table.columnViewportPosition(self.index.column()),
                                                                        self.table.rowViewportPosition(self.index.row()))))
            elif event.type() == QEvent.Leave:
                self.index = None
        return super(ForecastCalendarDialog, self).eventFilter(source, event)

    def handleCellEntered(self, index, pos):
        print(index.row(), index.column())
        pos += QPoint(25, 25)
        QToolTip.showText(pos, self.forecastedDayMapping[self.index.data()][0] + "\n" +
                                        self.forecastedDayMapping[self.index.data()][1], self, QRect(pos, QSize(20, 20)), 600_000_000)

    def markForecastOnCalendar(self):
        currentDayOfMonth = self.calendar.selectedDate().day()
        print("Forecasted days are: ")
        for i in range(1, len(self.forecast) + 1):
            print(f"{currentDayOfMonth + i}\n")
            markedDay = self.currentDay.addDays(i)

            weather = self.forecast[i - 1]['weather'][0]['main']
            format = QTextCharFormat()
            temperature = self.forecast[i - 1]['main']['temp']
            self.forecastedDayMapping[markedDay.day()] = (weather, str(temperature) + "°F", self.forecast[i - 1]['main'])

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
        for i in range(1, len(self.forecast) + 1):
            nextDay = self.currentDay.addDays(i)
            if date.day() == nextDay.day():
                forecastInfoDialog = ForecastInfoDialog(self.forecastedDayMapping[date.day()], date)
                forecastInfoDialog.exec()
        # if date.day() in range(self.currentDay.day() + 1, self.currentDay.day() + 6):
        #     print("Forecasted day was selected!")
        #     print(f"Forecast data for {self.calendar.monthShown()}/{date.day()}/{self.calendar.yearShown()}:"
        #           f"\nWeather: {self.forecast[date.day() - self.currentDay.day() - 1]['weather'][0]['main']}"
        #           f"\nTemperature: {self.forecast[date.day() - self.currentDay.day() - 1]['main']['temp']}")
        #     forecastInfoDialog = ForecastInfoDialog(self.forecastedDayMapping[date.day()], self)
        #     forecastInfoDialog.exec()

