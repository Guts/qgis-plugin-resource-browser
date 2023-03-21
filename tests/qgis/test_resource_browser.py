import unittest

from qgis.PyQt.QtWidgets import QWidget
from qgis.testing import start_app

from pyqgis_resource_browser.core.resource_table_model import ResourceTableModel
from pyqgis_resource_browser.gui.resource_browser import ResourceBrowser

app = start_app()


class ResourceBrowserTests(unittest.TestCase):
    def test_resource_browser(self):
        B = ResourceBrowser()
        self.assertIsInstance(B, QWidget)
        B.show()

        self.assertIsInstance(B.resourceModel, ResourceTableModel)

        # app.exec_()


if __name__ == "__main__":
    unittest.main(buffer=False)