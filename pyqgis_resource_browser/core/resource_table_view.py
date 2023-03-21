import os

from qgis.PyQt.QtCore import QModelIndex, Qt
from qgis.PyQt.QtGui import QContextMenuEvent, QPixmap
from qgis.PyQt.QtWidgets import QApplication, QMenu, QTableView


class ResourceTableView(QTableView):
    """
    A table view to visualize Qt resources
    """
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        idx = self.indexAt(event.pos())
        if isinstance(idx, QModelIndex) and idx.isValid():
            uri = idx.data(Qt.UserRole)
            m = QMenu()
            a = m.addAction("Copy Name")
            a.triggered.connect(
                lambda *args, n=os.path.basename(uri): QApplication.clipboard().setText(
                    n
                )
            )
            a = m.addAction("Copy Path")
            a.triggered.connect(
                lambda *args, n=uri: QApplication.clipboard().setText(n)
            )

            a = m.addAction("Copy Icon")
            a.triggered.connect(
                lambda *args, n=uri: QApplication.clipboard().setPixmap(QPixmap(n))
            )

            m.exec_(event.globalPos())

        pass
