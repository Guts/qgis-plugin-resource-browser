#! python3  # noqa: E265

"""
Plugin settings.
"""

# standard
from dataclasses import MISSING, asdict, dataclass, field, fields

# PyQGIS
from qgis.core import QgsSettings

# package
import pyqgis_resource_browser.toolbelt.log_handler as log_hdlr
from pyqgis_resource_browser.__about__ import __title__, __version__

# ############################################################################
# ########## Classes ###############
# ##################################


@dataclass
class PlgSettingsStructure:
    """Plugin settings structure and defaults values."""

    # global
    debug_mode: bool = False
    version: str = __version__

    # logic
    filter_prefixes: bool = True
    filter_filetypes: bool = True
    prefix_filters: list[str] = field(
        default_factory=lambda: [
            ":/geometrychecker/",
            ":/images/",
            ":/oauth2method/",
            ":/offline_editing/",
            ":/qt-project.org/",
            ":/topology",
        ]
    )

    filetype_filters: list[str] = field(
        default_factory=lambda: ["ico", "png", "svg", "xpn"]
    )

    # misc
    toolbar_browser_shortcut: bool = True


class PlgOptionsManager:
    """Class to deal with settings: get, set."""

    setting_keys = [f.name for f in fields(PlgSettingsStructure)]

    @staticmethod
    def get_plg_settings() -> PlgSettingsStructure:
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings
        :rtype: PlgSettingsStructure
        """
        # get dataclass fields definition
        settings_fields = fields(PlgSettingsStructure)

        # retrieve settings from QGIS/Qt
        settings = QgsSettings()
        settings.beginGroup(__title__)

        # map settings values to preferences object
        li_settings_values = []
        for i in settings_fields:
            try:
                li_settings_values.append(
                    settings.value(key=i.name, defaultValue=i.default, type=i.type)
                )
            except TypeError:
                defaultValue = (
                    i.default_factory() if i.default is MISSING else i.default
                )
                li_settings_values.append(
                    settings.value(key=i.name, defaultValue=defaultValue)
                )

        # instanciate new settings object
        options = PlgSettingsStructure(*li_settings_values)

        settings.endGroup()

        return options

    @staticmethod
    def get_value_from_key(key: str, default=None, exp_type=None):
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings value matching key
        """
        if key not in PlgOptionsManager.setting_keys:
            log_hdlr.PlgLogger.log(
                message="Bad settings key. Must be one of: {}".format(
                    ",".join(PlgOptionsManager.setting_keys)
                ),
                log_level=1,
            )
            return None

        settings = QgsSettings()
        settings.beginGroup(__title__)

        try:
            out_value = settings.value(key=key, defaultValue=default, type=exp_type)
        except Exception as err:
            log_hdlr.PlgLogger.log(
                message="Error occurred trying to get settings: {}.Trace: {}".format(
                    key, err
                )
            )
            out_value = None

        settings.endGroup()

        return out_value

    @classmethod
    def set_value_from_key(cls, key: str, value) -> bool:
        """Set plugin QSettings value using the key.

        :param key: QSettings key
        :type key: str
        :param value: value to set
        :type value: depending on the settings
        :return: operation status
        :rtype: bool
        """
        if key not in PlgOptionsManager.setting_keys:
            log_hdlr.PlgLogger.log(
                message=f"Bad settings key: {key}. Must be one of: "
                f"{','.join(PlgOptionsManager.setting_keys)}",
                log_level=2,
            )
            return False

        settings = QgsSettings()
        settings.beginGroup(__title__)

        try:
            settings.setValue(key, value)
            out_value = True
            log_hdlr.PlgLogger.log(
                f"Setting `{key}` saved with value `{value}`", log_level=4
            )
        except Exception as err:
            log_hdlr.PlgLogger.log(
                message=f"Error occurred trying to set settings: {key}.Trace: {err}"
            )
            out_value = False

        settings.endGroup()

        return out_value

    @classmethod
    def save_from_object(cls, plugin_settings_obj: PlgSettingsStructure):
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings value matching key
        """
        settings = QgsSettings()
        settings.beginGroup(__title__)

        for k, v in asdict(plugin_settings_obj).items():
            cls.set_value_from_key(k, v)

        settings.endGroup()
