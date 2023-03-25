import os
from typing import Any

from qgis.PyQt.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from qgis.PyQt.QtGui import QIcon

from . import scanResources


class ResourceTableFilterModel(QSortFilterProxyModel):
    """
    A QSortFilterProxyModel to filter resource strings
    """

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        # self.setRecursiveFilteringEnabled(True)
        # self.setFilterCaseSensitivity(Qt.CaseInsensitive)

        self.prefix_filters = []
        self.filetype_filters = []

    def setPrefixFilters(self, prefixes: list[str]):
        """
        Sets a list of prefixes. Each shown resource URI needs to have one of these.
        Use an empty list [] to disable prefix filtering.
        :param prefixes: List[str]
        """
        assert isinstance(prefixes, list)
        self.prefix_filters.clear()
        self.prefix_filters.extend(prefixes)
        self.invalidateFilter()

    def setFileTypeFilters(self, filetypes: list[str]):
        """
        Sets a list of filtetypes (or suffixes) that show resources should relate to.
        Use an empty list [] to disable filetype filtering.
        :param filetypes: List[str]
        """
        assert isinstance(filetypes, list)
        self.filetype_filters.clear()
        self.filetype_filters.extend(filetypes)
        self.invalidateFilter()

    def filterAcceptsRow(self, row: int, parent: QModelIndex) -> bool:
        b = super().filterAcceptsRow(row, parent)
        if b:
            uri: str = self.sourceModel().index(row, 0, parent).data(Qt.UserRole)
            if uri:
                if len(self.prefix_filters) > 0:
                    if not any(uri.startswith(f) for f in self.prefix_filters):
                        return False
                if len(self.filetype_filters) > 0:
                    if not any(uri.endswith(f) for f in self.filetype_filters):
                        return False
        return b


class ResourceTableModel(QAbstractTableModel):
    """
    A table model to show Qt resources
    """

    def __init__(self, *args, load_resources: bool = True, **kwds):
        """
        :param args:
        :param load_resources: set False to postpone resource loading until
                .reloadResources() is called explicitly.
        :param kwds:
        """
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
            resources = [
                f for r in resources for f in self.prefix_filters if r.startswith(f)
            ]
        if len(self.filetype_filters) > 0:
            resources = [
                f for r in resources for f in self.prefix_filters if r.endswith(f)
            ]

        self.RESOURCES.extend(resources)
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
