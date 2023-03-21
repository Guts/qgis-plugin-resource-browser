import unittest

from pyqgis_resource_browser.core.resource_table_model import ResourceTableModel
from pyqgis_resource_browser.gui.resource_browser import ResourceBrowser
from qgis.PyQt.QtWidgets import QWidget
from qgis.core import QgsApplication
from qgis.testing import start_app
start_app()

class ResourceBrowserTests(unittest.TestCase):

    def test_resource_browser(self):

        B = ResourceBrowser()
        self.assertIsInstance(B, QWidget)
        B.show()
        # uncomment to show the browser widget B
        QgsApplication.exec_()
        self.assertIsInstance(B.resourceModel, ResourceTableModel)


if __name__ == '__main__':
    unittest.main()
