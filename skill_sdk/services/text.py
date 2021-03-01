#
# voice-skill-sdk
#
# (C) 2020, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#

#
# Text service
#

import json
import time
import logging
import threading
from collections import defaultdict
from typing import DefaultDict, Dict, Union
import requests
from skill_sdk import l10n
from skill_sdk.caching.decorators import CallCache
from skill_sdk.caching.local import LocalTimeoutCache
from skill_sdk.config import config
from skill_sdk.services.base import BaseService
from skill_sdk.services.prometheus import prometheus_latency, partner_call
from .k8s import K8sChecks

# Default timeout when accessing text service
SERVICE_TEXT_TIMEOUT = 60

# Default update interval
SERVICE_TEXT_UPDATE_INTERVAL = 1 * 60

logger = logging.getLogger(__name__)

# Text service URL
config.read_environment('SERVICE_TEXT_URL', 'service-text', 'url')
# Timeout when accessing text service
config.read_environment('SERVICE_TEXT_TIMEOUT', 'service-text', 'timeout')
# Update interval
config.read_environment('SERVICE_TEXT_UPDATE_INTERVAL', 'service-text', 'update-interval')


def setup_service():
    """ Handle text services load/reload depending on a configuration value in `skill.conf`

        config.get("service-text", "load", fallback="auto"):

            "auto":     the translations are loaded at skill startup and reloaded at TEXT_SERVICE_UPDATE_INTERVAL
                        a skill will start without translations if text services are unavailable
                        (this is a default behaviour)

            "delayed":  the skill will start without translations and loads the catalog when requested by CVI
                        (i.e on a first invocation, if the translations are empty)

            "startup":  the translations are loaded at skill startup and reloaded at TEXT_SERVICE_UPDATE_INTERVAL
                        a skill will raise a l10n.TranslationError exception if text services are not available

            ""

    :return:
    """
    load = config.get("service-text", "load", fallback="auto")

    if load == 'auto':
        logger.info('Text services load=[auto], spawning translation workers...')
        # Load translations from text service
        threading.Thread(target=load_translations_from_server, args=(l10n.translations,), daemon=True).start()
        # Leave translations reload worker
        threading.Thread(target=translation_reload_worker, args=(l10n.translations,), daemon=True).start()

    if load == 'delayed':
        logger.info('Text services load=[delayed], waiting for request...')
        # Initialize with local translations or empty DelayedTranslations
        default_locales = [_.strip() for _ in config.get("service-text", "locales", fallback="de,fr").split(',')]

        locales = l10n.get_locales() or default_locales
        l10n.translations = {locale: DelayedTranslation(locale, l10n.get_translation(locale)) for locale in locales}

    if load == 'startup':
        logger.info('Text services load=[startup], loading translations...')
        # Load translations from text service and exit if not available
        if not load_translations_from_server(l10n.translations):
            logger.error('Text services not available. Exiting...')
            raise l10n.TranslationError('No translations found.')
        # Leave translations reload worker
        else:
            threading.Thread(target=translation_reload_worker, args=(l10n.translations, ), daemon=True).start()


class TextService(BaseService):
    """ Text (translation) service """

    VERSION = 1
    NAME = 'text'

    def __init__(self, headers=None):
        add_auth_header = config.getboolean("service-text", "auth_header", fallback=False)
        super().__init__(add_auth_header=add_auth_header, headers=headers)
        self.BASE_URL = f'{config.get("service-text", "url", fallback="http://service-text-service:1555")}'
        self.timeout = config.get("service-text", "timeout", fallback=SERVICE_TEXT_TIMEOUT)

    @property
    def scope(self):
        return config.get('i18n', 'scope', fallback=config.get('skill', 'name', fallback='unnamed-skill'))

    @CallCache([LocalTimeoutCache(60)])
    def supported_locales(self):
        locales = []

        with self.session as session:
            logger.debug('Requesting supported locales from server.')
            try:
                url = f'{self.url}/info/scope/{self.scope}'
                data = session.get(url).json()
                locales = [d['code'] for d in data['supportedLanguages']]
            except (KeyError, TypeError, json.decoder.JSONDecodeError, requests.exceptions.RequestException) as ex:
                logger.error(f"{self.url}/info/scope/{self.scope} responded with {ex}. Translation not available.")
        return locales

    @prometheus_latency('service-text.get_translation_catalog')
    def get_translation_catalog(self, locale):
        """ Get translation catalog for a particular locale

        :param locale:
        :return:
        """
        catalog: DefaultDict = defaultdict(list)

        with self.session as session:
            try:
                url = f'{self.url}/{locale}/{self.scope}'

                with partner_call(session.get, TextService.NAME) as get:
                    data = get(url).json()

                logger.debug('%s translation keys loaded.', len(data))
                for dataset in data:
                    for translation in dataset['sentences']:
                        catalog[dataset['tag']].append(translation)
            except (KeyError, TypeError, json.decoder.JSONDecodeError, requests.exceptions.RequestException) as ex:
                logger.error(f"{self.url}/{locale}/{self.scope} responded with {ex}. Catalog not available.")

        return dict(catalog)

    @prometheus_latency('service-text.get_full_catalog')
    def admin_get_full_catalog(self) -> dict:
        """ Get a complete translations catalog as {"language": {"key": "value"}} dictionary
            (admin route only!)

        :return:
        """
        catalog: DefaultDict = defaultdict(dict)

        with self.session as session:
            try:
                data = session.get(f'{self.url}/info/locale').json()
                locales = [locale['code'] for locale in data['supportedLanguages']
                           if l10n.RE_TRANSLATIONS.match(locale['code'])]
                logger.debug('Loading %s translation...', repr(locales))

                with partner_call(session.get, TextService.NAME) as get:
                    data = get(f'{self.url}/scope/{self.scope}').json()

                [catalog[_['locale']].update({_['tag']: _['sentences']}) for _ in data if _['locale'] in locales]

            except (KeyError, TypeError, json.decoder.JSONDecodeError, requests.exceptions.RequestException) as ex:
                logger.error(f"{self.url} responded with {ex}. Catalog not available.")

        return dict(catalog)


class ReloadableTranslation(l10n.MultiStringTranslation):
    """Translations with a scheduled reload"""

    def __init__(self, lang, translation: l10n.Translations = None) -> None:
        """
        Initialize an empty instance (optionally - with the catalog from an existing translation)

        @param locale:
        @param translation:
        """
        super().__init__(lang=lang)

        # Set catalog from local translation
        if translation is not None:
            self._catalog = {
                k: v if isinstance(v, list) else [v]
                for k, v in translation._catalog.items()
            }

    def reload(self):
        logger.debug('Reloading translations for %s.', self.lang)
        service = TextService()
        new_catalog = service.get_translation_catalog(self.lang)

        if new_catalog:
            logger.debug('Replacing old catalog for %s.', self.lang)
            K8sChecks.register_ready_check(f'load_i18n_{self.lang}')
            self._catalog = new_catalog
            K8sChecks.report_ready(f'load_i18n_{self.lang}')
        else:
            logger.warning('No translations found for %s.', self.lang)
            raise l10n.TranslationError(f'No translations found for {self.lang}.')


class DelayedTranslation(ReloadableTranslation):
    """A translation that is loaded on a user request"""

    def __init__(self, locale: str, translation: l10n.Translations = None) -> None:
        super().__init__(locale, translation)

        # Update interval (in seconds)
        self.update_interval: int = config.getint("service-text", "update-interval",
                                                  fallback=SERVICE_TEXT_UPDATE_INTERVAL)

        # Last reload timestamp
        self.last_reload: float = .0
        logger.debug('Delayed translation [%s] with update_interval=[%s].', self.lang, self.update_interval)

    def _check_catalog(self):
        logger.debug('Check delayed translation catalog [%s], last reload=[%s], '
                     'update interval=[%s].', self.lang, self.last_reload, self.update_interval)
        if not self._catalog:
            logger.debug('Catalog for %s is empty. Loading translations...', self.lang)
            try:
                translations = load_translations_from_server(l10n.translations)
                self._catalog = translations.get(self.lang)._catalog
            except AttributeError:
                logger.warning('No translations found for %s.', self.lang)
        elif time.time() - self.last_reload >= self.update_interval:
            # TODO: Start a thread, if this becomes a performance bottleneck
            self.reload()

    def reload(self):
        try:
            super().reload()
            self.last_reload = time.time()
            logger.debug('Finished reloading translations.')
        except l10n.TranslationError:
            pass

    def gettext(self, *args, **kwargs):
        self._check_catalog()
        return super().gettext(*args, **kwargs)

    def ngettext(self, *args, **kwargs):
        self._check_catalog()
        return super().ngettext(*args, **kwargs)

    def getalltexts(self, *args, **kwargs):
        self._check_catalog()
        return super().getalltexts(*args, **kwargs)


def translation_reload_worker(translations: Dict[Union[bytes, str], l10n.Translations]):
    """ Translations reload worker:
            reloads translations from the text service

    :param translations:
    :return:
    """
    update_interval = config.getfloat("service-text", "update-interval", fallback=SERVICE_TEXT_UPDATE_INTERVAL)
    logger.info('Translations reload worker started with %s sleep interval.', repr(update_interval))
    while True:
        time.sleep(update_interval)
        try:
            load_translations_from_server(translations, reload=True)
            logger.debug('Finished reloading translations.')
        except l10n.TranslationError:
            logger.error('Could not reload translations. Will try again in %s sec.', repr(update_interval))


def load_translations_from_server(translations: Dict[Union[bytes, str], l10n.Translations], reload: bool = False):
    """ Loads (or reloads) translations from the text services

    :param translations:
    :param reload:          reload flag, `False` - init call, `True` - reload call
    :return:
    """
    load = config.get("service-text", "load", fallback="startup")
    locale_class = DelayedTranslation if load == 'delayed' else ReloadableTranslation
    logger.debug("%s %s translations from text service.", 'Reloading' if reload else 'Loading', locale_class)

    service = TextService()

    # Get the list of supported locales
    locales = service.supported_locales()
    logger.debug("Available locales: %s", locales)

    for locale in locales:
        # Initialize translation object
        tr = locale_class(locale)

        # Load translations
        tr.reload()

        # Update the original
        translations.update({locale: tr})

    return translations
