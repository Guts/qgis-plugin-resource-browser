# standard lib
import os
import pathlib
import re

# PyQGIS
from qgis.core import QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QFile, QModelIndex, QRegExp, Qt, QTextStream, pyqtSignal
from qgis.PyQt.QtGui import QPixmap
from qgis.PyQt.QtSvg import QGraphicsSvgItem
from qgis.PyQt.QtWidgets import (
    QAction,
    QApplication,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QLabel,
    QLineEdit,
    QTextBrowser,
    QToolButton,
    QWidget,
)

# plugin
from ..core.resource_table_model import ResourceTableFilterModel, ResourceTableModel
from ..core.resource_table_view import ResourceTableView
from ..toolbelt import PlgOptionsManager


class ResourceGraphicsView(QGraphicsView):
    resized = pyqtSignal()

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.item = None

    def setItem(self, item):
        self.scene().clear()
        self.scene().addItem(item)
        self.item = item
        self.fitInView(item, Qt.KeepAspectRatio)

    def resizeEvent(self, QResizeEvent):
        if self.item:
            self.fitInView(self.item, Qt.KeepAspectRatio)


class ResourceBrowser(QWidget):
    """
    A widget to browser Qt resources, i.e. icons and text files.
    """

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        pathUi = pathlib.Path(__file__).parent / "resource_browser.ui"
        with open(pathUi.as_posix()) as uifile:
            uic.loadUi(uifile, baseinstance=self)

        self.setWindowTitle("Resource Browser")
        self.setWindowIcon(QgsApplication.getThemeIcon("mActionAddImage.svg"))
        self.actionReload: QAction
        self.optionUseRegex: QAction
        self.tbFilter: QLineEdit
        self.tableView: ResourceTableView
        self.btnUseRegex: QToolButton
        self.btnCaseSensitive: QToolButton
        self.btnReload: QToolButton
        self.preview: QLabel

        self.graphicsScene = QGraphicsScene()
        self.graphicsView: ResourceGraphicsView
        self.graphicsView.setScene(self.graphicsScene)

        self.textBrowser: QTextBrowser

        self.resourceModel: ResourceTableModel = ResourceTableModel()

        settings = PlgOptionsManager.get_plg_settings()

        self.resourceProxyModel = ResourceTableFilterModel()
        self.resourceProxyModel.setSourceModel(self.resourceModel)
        self.resourceProxyModel.setPrefixFilters(settings.prefix_filters)
        self.resourceProxyModel.setFileTypeFilters(settings.filetype_filters)
        self.resourceProxyModel.setFilterKeyColumn(0)
        self.resourceProxyModel.setFilterRole(Qt.UserRole)

        self.tableView.setSortingEnabled(True)
        self.tableView.setModel(self.resourceProxyModel)
        self.tableView.selectionModel().selectionChanged.connect(
            self.onSelectionChanged
        )

        self.btnReload.setDefaultAction(self.actionReload)
        self.btnUseRegex.setDefaultAction(self.optionUseRegex)
        self.btnCaseSensitive.setDefaultAction(self.optionCaseSensitive)
        self.actionReload.triggered.connect(self.resourceModel.reloadResources)

        self.optionCaseSensitive.toggled.connect(self.updateFilter)
        self.optionUseRegex.toggled.connect(self.updateFilter)
        self.tbFilter.textChanged.connect(self.updateFilter)

    def updateFilter(self):
        txt = self.tbFilter.text()

        expr = QRegExp(txt)

        if self.optionUseRegex.isChecked():
            expr.setPatternSyntax(QRegExp.RegExp)
        else:
            expr.setPatternSyntax(QRegExp.Wildcard)

        if self.optionCaseSensitive.isChecked():
            expr.setCaseSensitivity(Qt.CaseSensitive)
        else:
            expr.setCaseSensitivity(Qt.CaseInsensitive)

        if expr.isValid():
            self.resourceProxyModel.setFilterRegExp(expr)
            self.info.setText("")
        else:
            self.resourceProxyModel.setFilterRegExp(None)
            self.info.setText(expr.errorString())

    def onSelectionChanged(self, selected, deselected):
        selectedIdx = selected.indexes()
        if len(selectedIdx) == 0:
            self.updatePreview(None)
        else:
            idx1 = selectedIdx[0]
            assert isinstance(idx1, QModelIndex)

            uri = idx1.data(Qt.UserRole)
            self.updatePreview(uri)

    def updatePreview(self, uri: str):
        """
        Updates a preview
        """
        hasImage = False
        hasText = False
        self.textBrowser.clear()
        self.graphicsScene.clear()

        if isinstance(uri, str) and "." in uri:
            ext = os.path.splitext(uri)[1]

            item = None
            if ext == ".svg":
                item = QGraphicsSvgItem(uri)
            else:
                pm = QPixmap(uri)
                if not pm.isNull():
                    item = QGraphicsPixmapItem(pm)

            if item:
                hasImage = True
                self.graphicsView.setItem(item)

            if re.search(r"\.(svg|html|xml|txt|js|css)$", uri, re.I) is not None:
                file = QFile(uri)
                if file.open(QFile.ReadOnly | QFile.Text):
                    stream = QTextStream(file)
                    stream.setAutoDetectUnicode(True)
                    txt = stream.readAll()
                    self.textBrowser.setPlainText(txt)
                    hasText = True
                    file.close()

        self.tabWidget.setTabEnabled(self.tabWidget.indexOf(self.pageImage), hasImage)
        self.tabWidget.setTabEnabled(self.tabWidget.indexOf(self.pageText), hasText)

        # try to show a view that shows content
        if not self.tabWidget.widget(self.tabWidget.currentIndex()).isEnabled():
            for i in range(self.tabWidget.count()):
                if self.tabWidget.widget(i).isEnabled():
                    self.tabWidget.setCurrentIndex(i)
                    break

    def useFilterRegex(self) -> bool:
        return self.optionUseRegex.isChecked()


def showResources() -> ResourceBrowser:
    """
    A simple way to list available Qt resources
    :return:
    :rtype:
    """
    needQApp = not isinstance(QApplication.instance(), QApplication)
    if needQApp:
        QApplication([])
    browser = ResourceBrowser()
    browser.show()
    if needQApp:
        QApplication.instance().exec_()
    return browser
