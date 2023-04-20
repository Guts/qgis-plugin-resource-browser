# standard lib
import os
import re
from functools import partial
from pathlib import Path
from typing import Literal, Union

from qgis.core import QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QFile, QModelIndex, QRegExp, Qt, QTextStream, pyqtSignal
from qgis.PyQt.QtGui import QContextMenuEvent, QPixmap
from qgis.PyQt.QtSvg import QGraphicsSvgItem
from qgis.PyQt.QtWidgets import (
    QAction,
    QApplication,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QLabel,
    QLineEdit,
    QMenu,
    QTextBrowser,
    QToolButton,
    QWidget,
)

# PyQGIS
from qgis.utils import iface

# plugin
from pyqgis_resource_browser.__about__ import __title__
from pyqgis_resource_browser.core.resource_table_model import (
    ResourceTableFilterModel,
    ResourceTableModel,
)
from pyqgis_resource_browser.core.resource_table_view import ResourceTableView
from pyqgis_resource_browser.toolbelt import PlgLogger, PlgOptionsManager


class ResourceGraphicsView(QGraphicsView):
    resized = pyqtSignal()
    uri: str = ""

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.log = PlgLogger().log
        self.item = None

    def setItem(self, item: Union[QGraphicsSvgItem, QGraphicsPixmapItem]):
        """Set view item.

        :param item: _description_
        :type item: Union[QGraphicsSvgItem, QGraphicsPixmapItem]
        """
        self.scene().clear()
        self.scene().addItem(item)
        self.item = item
        self.fitInView(item, Qt.KeepAspectRatio)

    def resizeEvent(self, QResizeEvent):
        if self.item:
            self.fitInView(self.item, Qt.KeepAspectRatio)

    def contextMenuEvent(self, event: QContextMenuEvent):
        """Custom menu displayed on righ-click event on widget view.

        :param event: event that triggers the context-menu, typically right-click
        :type event: QContextMenuEvent
        """
        menu = QMenu(parent=self)

        # Copy image name
        action_copy_name = QAction(
            icon=QgsApplication.getThemeIcon("mIconLabelQuadrantOffset.svg"),
            text=self.tr("Copy name"),
            parent=self,
        )
        action_copy_name.triggered.connect(partial(self.copy_to_clipboard, "name"))

        # Copy image path
        action_copy_path = QAction(
            icon=QgsApplication.getThemeIcon("mIconFileLink.svg"),
            text=self.tr("Copy path"),
            parent=self,
        )
        action_copy_path.triggered.connect(partial(self.copy_to_clipboard, "path"))

        # Copy as getThemeIcon syntax
        action_copy_theme_icon = QAction(
            icon=QgsApplication.getThemeIcon("mActionEditInsertImage.svg"),
            text=self.tr("Copy as getThemeIcon syntax"),
            parent=self,
        )
        action_copy_theme_icon.triggered.connect(
            partial(self.copy_to_clipboard, "getThemeIcon")
        )

        # Copy as QIcon syntax
        action_copy_qicon = QAction(
            icon=QgsApplication.getThemeIcon("mActionEditCopy.svg"),
            text=self.tr("Copy as QIcon syntax"),
            parent=self,
        )
        action_copy_qicon.triggered.connect(partial(self.copy_to_clipboard, "qicon"))

        # Copy as QPixmap syntax
        action_copy_qpixmap = QAction(
            icon=QgsApplication.getThemeIcon("mIconColorPicker.svg"),
            text=self.tr("Copy as QPixmap syntax"),
            parent=self,
        )
        action_copy_qpixmap.triggered.connect(
            partial(self.copy_to_clipboard, "qpixmap")
        )

        # add actions to context menu
        menu.addAction(action_copy_name)
        menu.addAction(action_copy_path)
        menu.addSeparator()
        menu.addAction(action_copy_theme_icon)
        menu.addAction(action_copy_qicon)
        menu.addAction(action_copy_qpixmap)

        # open the menu at the event global position
        menu.exec_(event.globalPos())

    def copy_to_clipboard(
        self,
        expected_format: Literal["getThemeIcon", "name", "path", "qicon", "qpixmap"],
    ) -> str:
        """Copy item uri to system clipboard in an expected format.

        :param expected_format: expected format
        :type expected_format: Literal[&quot;name&quot;, &quot;path&quot;, &quot;qicon&quot;, &quot;qpixmap&quot;]

        :return: formatted uri in the expected format
        :rtype: str
        """
        self.log(
            message=f"DEBUG - Copy to clipboard {self.uri} in {expected_format} format.",
            log_level=4,
        )
        if expected_format.lower() == "name":
            QApplication.clipboard().setText(Path(self.uri).name)
            self.log(message=f"Text copied: {Path(self.uri).name}", log_level=4)
            return Path(self.uri).name
        if expected_format.lower() == "path":
            QApplication.clipboard().setText(self.uri)
            self.log(message=f"Text copied: {self.uri}", log_level=4)
            return self.uri
        if expected_format.lower() == "getthemeicon":
            QApplication.clipboard().setText(
                f"QgsApplication.getThemeIcon('{Path(self.uri).name}')"
            )
            self.log(
                message=f"Text copied: QgsApplication.getThemeIcon('{Path(self.uri).name}')",
                log_level=4,
            )
            return f"QgsApplication.getThemeIcon('{self.uri}')"
        if expected_format.lower() == "qpixmap":
            QApplication.clipboard().setText(f"QPixmap('{self.uri}')")
            self.log(message=f"Text copied: QPixmap('{self.uri}')", log_level=4)
            return f"QPixmap('{self.uri}')"
        if expected_format.lower() == "qicon":
            QApplication.clipboard().setText(f"QIcon('{self.uri}')")
            self.log(message=f"Text copied: QIcon('{self.uri}')", log_level=4)
            return f"QIcon('{self.uri}')"

        self.log(message=f"Undefined format: {expected_format}", push=True, log_level=1)


class ResourceBrowser(QWidget):
    """
    A widget to browser Qt resources, i.e. icons and text files.
    """

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        pathUi = Path(__file__).parent / "resource_browser.ui"
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

        self.resourceProxyModel = ResourceTableFilterModel()
        self.resourceProxyModel.setSourceModel(self.resourceModel)
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

        # settings button
        self.btn_settings.setToolTip(self.tr("Settings"))
        self.btn_settings.setText("")
        self.btn_settings.setIcon(
            QgsApplication.getThemeIcon("console/iconSettingsConsole.svg")
        )
        self.btn_settings.pressed.connect(
            partial(iface.showOptionsDialog, currentPage=f"mOptionsPage{__title__}")
        )

        self.slot_config_changed()

    def slot_config_changed(self):
        """When settings have been saved."""
        settings = PlgOptionsManager.get_plg_settings()
        if settings.filter_prefixes:
            self.resourceProxyModel.setPrefixFilters(settings.prefix_filters)
        else:
            self.resourceProxyModel.setPrefixFilters([])

        if settings.filter_filetypes:
            self.resourceProxyModel.setFileTypeFilters(settings.filetype_filters)
        else:
            self.resourceProxyModel.setFileTypeFilters([])

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
                self.graphicsView.uri = uri

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
