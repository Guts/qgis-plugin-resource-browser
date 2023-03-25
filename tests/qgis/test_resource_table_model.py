#! python3  # noqa E265

"""
    Usage from the repo root folder:

    .. code-block:: bash

        # for whole tests
        python -m unittest tests.qgis.test_resource_table_model
        # for specific test
        python -m unittest tests.qgis.test_resource_table_model.TestResourceTableModel.test_resource_table_model
"""

# standard library
# import unittest

from qgis.PyQt.Qt import Qt
from qgis.testing import unittest

from pyqgis_resource_browser.core.resource_table_model import (
    ResourceTableFilterModel,
    ResourceTableModel,
)

# ############################################################################
# ########## Classes #############
# ################################


class TestResourceTableModel(unittest.TestCase):
    def test_resource_table_model(self):
        m = ResourceTableModel(load_resources=False)

        self.assertEqual(len(m), 0)
        m.reloadResources()
        n = len(m)
        self.assertTrue(n > 0)

        fm = ResourceTableFilterModel()
        fm.setSourceModel(m)
        self.assertEqual(fm.rowCount(), n)

        fm.setFileTypeFilters(["svg"])
        self.assertTrue(fm.rowCount() < n)
        for row in range(fm.rowCount()):
            uri = fm.index(row, 0).data(Qt.UserRole)
            self.assertIsInstance(uri, str)
            self.assertTrue(uri.endswith("svg"))

        fm.setFileTypeFilters([])
        fm.setPrefixFilters([":/images/"])
        for row in range(fm.rowCount()):
            uri = fm.index(row, 0).data(Qt.UserRole)
            self.assertTrue(uri.startswith(":/images/"))


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
