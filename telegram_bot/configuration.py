"""
Questo modulo contiene utility e dati di configurazione dell'applicazione.
"""
import os
import typing
import logging


log = logging.getLogger(__name__)


class MissingSettingError(Exception):
    """
    Eccezione sollevata quando :func:`.setting` non può venir trovata.
    """

    def __init__(self, name: str) -> None:
        self.name: str = name

    def __str__(self) -> str:
        return f"Neither {self.name} or {self.name}_FILENAME are set, and the setting is required"


def setting_required(name) -> str:
    """
    Tenta di leggere l'envar di nome ``name`` da:
    - I contenuti del file nell'envar ``{name}_FILENAME``.
    - I contenuti dell'envar ``{name}``.
    :raises .MissingSettingError: se non trova nulla, solleva questa eccezione.
    """

    log.debug(f"Reading setting with name {name}")

    if setting_filename := os.environ.get(f"{name}_FILENAME"):
        log.debug(f"Setting {name} is set via filename at {setting_filename}")
        with open(setting_filename) as file:
            setting = file.read().strip()
    elif setting := os.environ.get(f"{name}"):
        log.debug(f"Setting {name} is set via environment variable")
    else:
        raise MissingSettingError(name)

    return setting


def setting_optional(name) -> typing.Optional[str]:
    """
    Come :func:`.setting`, ma restituisce :data:`None` anzichè sollevare un'eccezione.
    """

    try:
        return setting_required(name)
    except MissingSettingError:
        return None


# Variabili d'ambiente necessarie
BOT_TOKEN = setting_required("BOT_TOKEN")
ADMIN_USERNAME = setting_required("ADMIN_USERNAME")
ADMIN_PASSWORD = setting_required("ADMIN_PASSWORD")
CHAT_ID = setting_required("CHAT_ID")
