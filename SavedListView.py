from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *



class SavedListView(QAbstractListModel):
    def __init__(self, locations, parent=None):
        super().__init__(parent)
        self.locations = locations

    def parent(self):
        return QModelIndex()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.locations)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self.locations[index.row()].location
        if role == Qt.UserRole:
            return self.locations[index]
        return QVariant()


