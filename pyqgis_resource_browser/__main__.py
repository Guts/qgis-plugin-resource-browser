# -*- coding: utf-8 -*-

"""
***************************************************************************
    __main__
    ---------------------
    Date                 : March 2023
    Copyright            : (C) 2023 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
**************************************************************************
"""

from pyqgis_resource_browser.gui.resource_browser import ResourceBrowser
from qgis.core import QgsApplication
from qgis.gui import QgisInterface
from qgis.testing.mocked import get_iface

iface: QgisInterface = None


def run():
    """
    Starts Resource Browser GUI from python
    """
    global iface
    # has_qapp: bool = isinstance(QgsApplication.instance(), QgsApplication)
    iface = get_iface()
    browser = ResourceBrowser()
    browser.show()
    QgsApplication.instance().exec_()


if __name__ == '__main__':
    # todo: add arguments that are helpful for testing, e.g. to inspect *_rc.py and *.qrc files
    # parser = argparse.ArgumentParser(description='Start the Resource Browser')
    # args = parser.parse_args()
    run()
