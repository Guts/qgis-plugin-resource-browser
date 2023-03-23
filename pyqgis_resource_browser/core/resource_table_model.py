import os
from typing import Any, List

from qgis.PyQt.QtCore import QAbstractTableModel, QModelIndex, Qt
from qgis.PyQt.QtGui import QIcon

from . import scanResources


class ResourceTableModel(QAbstractTableModel):
    """
    A table model to show Qt resources
    """

    def __init__(self, *args, load_resources: bool = True, **kwds):
        super().__init__(*args, **kwds)

        self.cnUri = "Path"
        self.cnIcon = "Resource"
        self.RESOURCES = []

        self.prefix_filters = []
        self.filetype_filters = []

        if load_resources:
            self.reloadResources()

    def __len__(self):
        return self.rowCount()

    def reloadResources(self):
        """
        Call this to reload all Qt resources
        """
        self.beginResetModel()
        self.RESOURCES.clear()
        resources = list(scanResources())

        # filter available resource domains and file types
        if len(self.prefix_filters) > 0:
            resources = [f for r in resources for f in self.prefix_filters if r.startswith(f)]
        if len(self.filetype_filters) > 0:
            resources = [f for r in resources for f in self.prefix_filters if r.endswith(f)]

        self.RESOURCES.extend(resources)
        self.endResetModel()

    def setPrefixFilters(self, prefixes: List[str]):
        assert isinstance(prefixes, list)
        self.prefix_filters.clear()
        self.prefix_filters.extend(prefixes)
        self.reloadResources()

    def setFileTypeFilters(self, filetypes: List[str]):
        assert isinstance(filetypes, list)
        self.filetype_filters.clear()
        self.filetype_filters.extend(filetypes)
        self.reloadResources()

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
