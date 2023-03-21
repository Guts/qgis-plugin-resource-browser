import os
from typing import Any

from . import scanResources
from qgis.PyQt.QtCore import QAbstractTableModel, QModelIndex, Qt
from qgis.PyQt.QtGui import QIcon


class ResourceTableModel(QAbstractTableModel):
    """
    A table model to show Qt resources
    """
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.cnUri = "Path"
        self.cnIcon = "Resource"
        self.RESOURCES = []
        self.reloadResources()

    def reloadResources(self):
        """
        Call this to reload all Qt resources
        """
        self.beginResetModel()
        self.RESOURCES.clear()
        self.RESOURCES.extend(list(scanResources()))
        self.endResetModel()

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 2

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.RESOURCES)

    def columnNames(self) -> list[str]:
        return [self.cnUri, self.cnIcon]

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = ...
    ) -> Any:
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.columnNames()[section]

        if role == Qt.TextAlignmentRole and orientation == Qt.Vertical:
            return Qt.AlignRight

        return super().headerData(section, orientation, role)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return None

        uri = self.RESOURCES[index.row()]
        cn = self.columnNames()[index.column()]

        if role == Qt.DisplayRole:
            if cn == self.cnUri:
                return uri
            else:
                return os.path.basename(uri)
        if role == Qt.DecorationRole:
            if cn == self.cnIcon:
                return QIcon(uri)

        if role == Qt.ToolTipRole:
            if cn == self.cnUri:
                return uri

        if role == Qt.UserRole:
            return uri

        return None
