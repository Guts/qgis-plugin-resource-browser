#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash

    # for whole tests
    python -m unittest tests.qgis.test_plg_preferences
    # for specific test
    python -m unittest tests.qgis.test_plg_preferences.TestPlgPreferences.test_plg_preferences_structure
"""
from PyQt5.QtGui import QIcon
from qgis.gui import QgsOptionsDialogBase
from qgis.PyQt.Qt import Qt

# standard library
from qgis.testing import start_app, unittest

# project
from pyqgis_resource_browser.__about__ import __version__
from pyqgis_resource_browser.gui.dlg_settings import (
    ConfigOptionsPage,
    PlgOptionsFactory,
)
from pyqgis_resource_browser.toolbelt import PlgOptionsManager
from pyqgis_resource_browser.toolbelt.preferences import PlgSettingsStructure

app = start_app()
# ############################################################################
# ########## Classes #############
# ################################


class TestOptionsDialog(QgsOptionsDialogBase):
    def __init__(self, parent=None):
        super(QgsOptionsDialogBase, self).__init__(
            "PROPERTIES", parent, Qt.Dialog, settings=None
        )
        self.initOptionsBase(False, "PROPERTIES")


class TestPlgPreferences(unittest.TestCase):
    def test_plg_preferences_structure(self):
        """Test settings types and default values."""
        settings = PlgSettingsStructure()

        # global
        self.assertTrue(hasattr(settings, "debug_mode"))
        self.assertIsInstance(settings.debug_mode, bool)
        self.assertEqual(settings.debug_mode, False)

        self.assertTrue(hasattr(settings, "version"))
        self.assertIsInstance(settings.version, str)
        self.assertEqual(settings.version, __version__)

    def test_dlg_settings(self):
        factory = PlgOptionsFactory()
        page = factory.createWidget(None)
        self.assertIsInstance(factory.title(), str)
        self.assertIsInstance(factory.icon(), QIcon)
        self.assertIsInstance(page, ConfigOptionsPage)
        page.te_resource_prefixes.setPlainText("")
        page.apply()
        settings = PlgOptionsManager.get_plg_settings()
        self.assertEqual(settings.prefix_filters, [])
        page.reset_settings()
        settings = PlgOptionsManager.get_plg_settings()
        self.assertTrue(len(settings.prefix_filters) > 0)
        page.show()
        # app.exec_()


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
