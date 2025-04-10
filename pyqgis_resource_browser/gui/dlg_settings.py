#! python3  # noqa: E265

"""
Plugin settings form integrated into QGIS 'Options' menu.
"""

# standard
from functools import partial
from pathlib import Path

# PyQGIS
from qgis.core import QgsApplication
from qgis.gui import QgsOptionsPageWidget, QgsOptionsWidgetFactory
from qgis.PyQt import uic
from qgis.PyQt.Qt import QUrl
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtGui import QDesktopServices, QIcon

# project
from pyqgis_resource_browser.__about__ import (
    __icon_path__,
    __title__,
    __uri_homepage__,
    __uri_tracker__,
    __version__,
)
from pyqgis_resource_browser.toolbelt import PlgLogger, PlgOptionsManager
from pyqgis_resource_browser.toolbelt.preferences import PlgSettingsStructure

# ############################################################################
# ########## Globals ###############
# ##################################

FORM_CLASS, _ = uic.loadUiType(Path(__file__).parent / f"{Path(__file__).stem}.ui")


# ############################################################################
# ########## Classes ###############
# ##################################


class ConfigOptionsPage(FORM_CLASS, QgsOptionsPageWidget):
    """Settings form embedded into QGIS 'options' menu."""

    configChanged = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.log = PlgLogger().log
        self.plg_settings = PlgOptionsManager()

        # load UI and set objectName
        self.setupUi(self)
        self.setObjectName(f"mOptionsPage{__title__}")

        # header
        self.lbl_title.setText(f"{__title__} - Version {__version__}")

        # customization
        self.btn_help.setIcon(QIcon(QgsApplication.iconPath("mActionHelpContents.svg")))
        self.btn_help.pressed.connect(
            partial(QDesktopServices.openUrl, QUrl(__uri_homepage__))
        )

        self.btn_report.setIcon(
            QIcon(QgsApplication.iconPath("console/iconSyntaxErrorConsole.svg"))
        )
        self.btn_report.pressed.connect(
            partial(QDesktopServices.openUrl, QUrl(f"{__uri_tracker__}/new/choose"))
        )

        self.btn_reset.setIcon(QIcon(QgsApplication.iconPath("mActionUndo.svg")))
        self.btn_reset.pressed.connect(self.reset_settings)

        # load previously saved settings
        self.load_settings()

    def apply(self):
        """Called to permanently apply the settings shown in the options page (e.g. \
        save them to QgsSettings objects). This is usually called when the options \
        dialog is accepted."""
        settings = self.plg_settings.get_plg_settings()

        # misc
        settings.debug_mode = self.opt_debug.isChecked()
        settings.toolbar_browser_shortcut = (
            self.opt_toolbar_browser_shortcut.isChecked()
        )
        settings.version = __version__

        prefix_filters = self.te_resource_prefixes.toPlainText().strip().split("\n")
        filetype_filters = self.te_resource_filetypes.toPlainText().strip().split("\n")
        settings.prefix_filters = [f for f in prefix_filters if f != ""]
        settings.filetype_filters = [f for f in filetype_filters if f != ""]
        settings.filter_filetypes = self.gb_filter_resourcefiletype.isChecked()
        settings.filter_prefixes = self.gb_filter_resourceprefix.isChecked()

        # dump new settings into QgsSettings
        self.plg_settings.save_from_object(settings)

        if __debug__:
            self.log(
                message="DEBUG - Settings successfully saved.",
                log_level=4,
            )
        self.configChanged.emit()

    def load_settings(self):
        """Load options from QgsSettings into UI form."""
        settings = self.plg_settings.get_plg_settings()

        # global
        self.opt_debug.setChecked(settings.debug_mode)
        self.opt_toolbar_browser_shortcut.setChecked(settings.toolbar_browser_shortcut)
        self.lbl_version_saved_value.setText(settings.version)

        self.gb_filter_resourceprefix.setChecked(settings.filter_prefixes)
        self.gb_filter_resourcefiletype.setChecked(settings.filter_filetypes)

        self.te_resource_prefixes.setPlainText("\n".join(settings.prefix_filters))
        self.te_resource_filetypes.setPlainText("\n".join(settings.filetype_filters))

    def reset_settings(self):
        """Reset settings to default values (set in preferences.py module)."""
        default_settings = PlgSettingsStructure()

        # dump default settings into QgsSettings
        self.plg_settings.save_from_object(default_settings)

        # update the form
        self.load_settings()
        self.configChanged.emit()


class PlgOptionsFactory(QgsOptionsWidgetFactory):
    """Factory for options widget."""

    configChanged = pyqtSignal()

    def __init__(self):
        """Constructor."""
        super().__init__()

    def icon(self) -> QIcon:
        """Returns plugin icon, used to as tab icon in QGIS options tab widget.

        :return: _description_
        :rtype: QIcon
        """
        return QIcon(str(__icon_path__))

    def createWidget(self, parent) -> ConfigOptionsPage:
        """Create settings widget.

        :param parent: Qt parent where to include the options page.
        :type parent: QObject

        :return: options page for tab widget
        :rtype: ConfigOptionsPage
        """
        page = ConfigOptionsPage(parent)
        page.configChanged.connect(self.configChanged.emit)
        return page

    def title(self) -> str:
        """Returns plugin title, used to name the tab in QGIS options tab widget.

        :return: plugin title from about module
        :rtype: str
        """
        return __title__

    def helpId(self) -> str:
        """Returns plugin help URL.

        :return: plugin homepage url from about module
        :rtype: str
        """
        return __uri_homepage__
