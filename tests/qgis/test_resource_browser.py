#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash

    # for whole tests
    python -m unittest tests.qgis.test_resource_browser
    # for specific test
    python -m unittest tests.qgis.test_resource_browser.TestResourceBrowser.test_resource_browser
"""

# standard library
# import unittest

from qgis.PyQt.QtWidgets import QWidget
from qgis.testing import start_app, unittest

from pyqgis_resource_browser.core.resource_table_model import ResourceTableModel
from pyqgis_resource_browser.gui.resource_browser import ResourceBrowser

# create a QgsApplication(QApplication)
app = start_app()

# ############################################################################
# ########## Classes #############
# ################################


class TestResourceBrowser(unittest.TestCase):
    def test_resource_browser(self):
        B = ResourceBrowser()
        self.assertIsInstance(B, QWidget)
        B.show()
        # uncomment to show the browser widget B
        # app.exec_()
        self.assertIsInstance(B.resourceModel, ResourceTableModel)


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
