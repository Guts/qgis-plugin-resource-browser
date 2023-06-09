from collections.abc import Generator

from qgis.PyQt.QtCore import QDirIterator


def scanResources(path: str = ":") -> Generator[str, None, None]:
    """Recursively returns Qt resource paths.
    Can be used to scan directories for file paths as well"""
    D = QDirIterator(path)
    while D.hasNext():
        entry = D.next()
        if D.fileInfo().isDir():
            yield from scanResources(path=entry)
        elif D.fileInfo().isFile():
            yield D.filePath()
