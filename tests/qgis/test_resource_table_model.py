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

from pyqgis_resource_browser.core.resource_table_model import ResourceTableModel
from qgis.testing import unittest, start_app

start_app()


# ############################################################################
# ########## Classes #############
# ################################


class TestResourceTableModel(unittest.TestCase):
    def test_resource_table_model(self):
        m = ResourceTableModel(load_resources=False)

        self.assertEqual(len(m), 0)
        m.reloadResources()
        self.assertTrue(len(m) > 0)

        m.setFileTypeFilters(['svg'])
        for r in m.RESOURCES:
            self.assertTrue(r.endswith('svg'))

        m.setFileTypeFilters([])
        m.setPrefixFilters([':/images/'])
        for r in m.RESOURCES:
            self.assertTrue(r.startswith(':/images/'))


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
