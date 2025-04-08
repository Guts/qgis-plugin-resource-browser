#! python3  # noqa: E265

"""
Main plugin module.
"""

# standard lib
from functools import partial
from pathlib import Path

from qgis.core import QgsApplication, QgsSettings
from qgis.gui import QgisInterface

# PyQGIS
from qgis.PyQt.QtCore import QCoreApplication, QLocale, QTranslator, QUrl
from qgis.PyQt.QtGui import QDesktopServices, QIcon
from qgis.PyQt.QtWidgets import QAction

# project
from pyqgis_resource_browser.__about__ import (
    DIR_PLUGIN_ROOT,
    __icon_path__,
    __title__,
    __uri_homepage__,
    __uri_related_website__,
)
from pyqgis_resource_browser.gui.dlg_settings import PlgOptionsFactory
from pyqgis_resource_browser.gui.resource_browser import ResourceBrowser
from pyqgis_resource_browser.toolbelt import PlgLogger, PlgOptionsManager

# ############################################################################
# ########## Classes ###############
# ##################################


class PlgPyQgisResourceBrowserPlugin:
    def __init__(self, iface: QgisInterface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class which \
        provides the hook by which you can manipulate the QGIS application at run time.
        :type iface: QgsInterface
        """
        # set attributes
        self.action_browse_resources = None
        self.action_help = None
        self.action_help_plugin_menu_cheatsheet = None
        self.action_help_plugin_menu_documentation = None
        self.action_settings = None
        self.action_toolbar = None
        self.browser: ResourceBrowser = None
        self.options_factory: PlgOptionsFactory = None
        self.iface = iface
        self.log = PlgLogger().log
        self.plg_settings = PlgOptionsManager()

        # initialize the locale
        self.locale: str = QgsSettings().value("locale/userLocale", QLocale().name())[
            0:2
        ]
        locale_path: Path = (
            DIR_PLUGIN_ROOT / f"resources/i18n/pyqgis_resource_browser_{self.locale}.qm"
        )
        self.log(message=f"Translation: {self.locale}, {locale_path}", log_level=4)
        if locale_path.exists():
            self.translator = QTranslator()
            self.translator.load(str(locale_path.resolve()))
            QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        """Set up plugin UI elements."""
        settings = self.plg_settings.get_plg_settings()

        # settings page within the QGIS preferences menu
        if not self.options_factory:
            self.options_factory = PlgOptionsFactory()
            self.iface.registerOptionsWidgetFactory(self.options_factory)

        # -- Actions
        self.action_browse_resources = QAction(
            QgsApplication.getThemeIcon("mActionAddImage.svg"),
            self.tr("Browse resources"),
            self.iface.mainWindow(),
        )
        self.action_browse_resources.triggered.connect(self.run)

        self.action_help = QAction(
            QgsApplication.getThemeIcon("mActionHelpContents.svg"),
            self.tr("Documentation"),
            self.iface.mainWindow(),
        )
        self.action_help.triggered.connect(
            partial(QDesktopServices.openUrl, QUrl(__uri_homepage__))
        )

        self.action_settings = QAction(
            QgsApplication.getThemeIcon("console/iconSettingsConsole.svg"),
            self.tr("Settings"),
            self.iface.mainWindow(),
        )
        self.action_settings.triggered.connect(
            lambda: self.iface.showOptionsDialog(currentPage=f"mOptionsPage{__title__}")
        )

        # -- Menu
        self.iface.addPluginToMenu(__title__, self.action_browse_resources)
        self.iface.addPluginToMenu(__title__, self.action_settings)
        self.iface.addPluginToMenu(__title__, self.action_help)

        # -- Toolbar
        if settings.toolbar_browser_shortcut and not self.action_toolbar:
            self.action_toolbar = self.action_browse_resources
            self.iface.addToolBarIcon(self.action_toolbar)

        # -- Help menu

        # documentation
        self.iface.pluginHelpMenu().addSeparator()
        self.action_help_plugin_menu_documentation = QAction(
            QIcon(str(__icon_path__)),
            f"{__title__} - Documentation",
            self.iface.mainWindow(),
        )
        self.action_help_plugin_menu_documentation.triggered.connect(
            partial(QDesktopServices.openUrl, QUrl(__uri_homepage__))
        )

        self.iface.pluginHelpMenu().addAction(
            self.action_help_plugin_menu_documentation
        )

        # PyQGIS Icons Cheatsheet website
        self.action_help_plugin_menu_cheatsheet = QAction(
            QIcon(f"{DIR_PLUGIN_ROOT}/resources/images/pyqgis.png"),
            "PyQGIS Icons Cheatsheet",
            self.iface.mainWindow(),
        )
        self.action_help_plugin_menu_cheatsheet.triggered.connect(
            partial(QDesktopServices.openUrl, QUrl(__uri_related_website__))
        )

        self.iface.pluginHelpMenu().addAction(self.action_help_plugin_menu_cheatsheet)

    def slot_config_changed(self):
        """When settings have been saved."""
        settings = self.plg_settings.get_plg_settings()

        # toolbar icon or not
        if settings.toolbar_browser_shortcut and not self.action_toolbar:
            self.action_toolbar = self.action_browse_resources
            self.iface.addToolBarIcon(self.action_toolbar)
            self.log(
                message="DEBUG - Config changed: toolbar shortcut has been enabled.",
                log_level=4,
            )
        elif not settings.toolbar_browser_shortcut and self.action_toolbar:
            self.iface.removeToolBarIcon(self.action_toolbar)
            self.action_toolbar = None
            self.log(
                message="DEBUG - Config changed: toolbar shortcut has been removed.",
                log_level=4,
            )

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def unload(self):
        """Cleans up when plugin is disabled/uninstalled."""
        # -- Clean up menu
        self.iface.removePluginMenu(__title__, self.action_browse_resources)
        self.iface.removePluginMenu(__title__, self.action_help)
        self.iface.removePluginMenu(__title__, self.action_settings)

        # -- Clean up help menu
        self.iface.pluginHelpMenu().removeAction(
            self.action_help_plugin_menu_documentation
        )
        self.iface.pluginHelpMenu().removeAction(
            self.action_help_plugin_menu_cheatsheet
        )

        # -- Clean up toolbar
        if self.action_toolbar:
            self.iface.removeToolBarIcon(self.action_toolbar)
            self.action_toolbar = None

        # -- Clean up preferences panel in QGIS settings
        self.iface.unregisterOptionsWidgetFactory(self.options_factory)

        # remove actions
        del self.action_browse_resources
        del self.action_settings
        del self.action_help

    def run(self):
        """Main process.

        :raises Exception: if there is no item in the feed
        """
        try:
            if not isinstance(self.browser, ResourceBrowser):
                self.browser = ResourceBrowser()
                self.options_factory.configChanged.connect(
                    self.browser.slot_config_changed
                )
                self.options_factory.configChanged.connect(self.slot_config_changed)
            self.browser.show()
            self.log(
                message="Everything ran OK.",
                log_level=3,
                push=False,
            )
        except Exception as err:
            self.log(
                message=f"Houston, we've got a problem: {err}",
                log_level=2,
                push=True,
                duration=60,
                button=True,
            )
