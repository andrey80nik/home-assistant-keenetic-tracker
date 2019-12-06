"""
Support for Keenetic routers.
"""
import logging
import voluptuous as vol
import re
import homeassistant.helpers.config_validation as cv
from homeassistant.components.device_tracker import (
    DOMAIN, PLATFORM_SCHEMA, CONF_SCAN_INTERVAL, DeviceScanner)
from homeassistant.const import CONF_URL, CONF_PASSWORD, CONF_USERNAME

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_URL, default='http://192.168.1.1/'): cv.string,
    vol.Optional(CONF_USERNAME, default='admin'): cv.string,
    vol.Optional(CONF_PASSWORD, default='admin'): cv.string,
})


def get_scanner(hass, config):
    """Validate the configuration and return KeeneticDeviceScanner."""
    _LOGGER.debug('Keenetic init')
    scanner = KeeneticDeviceScanner(config[DOMAIN])
    return scanner if scanner.success_init else None


class KeeneticDeviceScanner(DeviceScanner):
    """This class queries a Keenetic router."""

    def __init__(self, config):
        """Initialize the scanner."""
        self.last_results = None
        self.url = config[CONF_URL]
        self.username = config[CONF_USERNAME]
        self.password = config[CONF_PASSWORD]
        self.scan_interval = config[CONF_SCAN_INTERVAL]
        self.last_results = []


        r = self._request()
        self.success_init = True if 'text' in r else False

        if self.success_init:
            _LOGGER.info('Successfully connected to Keenetic router')
            if 'error_id' in r:
                _LOGGER.info('But %s', r['error_msg'])
        else:
            _LOGGER.error('Failed to connect to Keenetic router: %s', r['error_msg'])

    def scan_devices(self):
        self._update_info()
        _LOGGER.debug('active_hosts %s', str(self.last_results))
        return self.last_results

    def get_device_name(self, mac):
        return None

    def _request(self, timeout=5):
        import requests
        from requests.auth import HTTPDigestAuth
        from requests.exceptions import HTTPError, ConnectionError, RequestException

        headers = {'Content-Type': 'application/xml'}
        xml= '<request><command name="show ip hotspot"/></request>'
        error_id = None
        error_msg = None
        r = None

        try:
            r = requests.post(
                self.url + 'ci',
                auth=HTTPDigestAuth(self.username, self.password),
                timeout=timeout,
                headers=headers,
                data=xml)
            r.raise_for_status()
        except HTTPError as e:
            error_id = 'status'
            error_msg = 'Bad status: ' + str(e)
        except ConnectionError as e:
            error_id = 'connection'
            error_msg = "Can't connect to router: " + str(e)
        except RequestException as e:
            error_id = 'other'
            error_msg = 'Some error during request: ' + str(e)
        return {'error_id': error_id, 'error_msg': error_msg} if error_id else {'text': r.text}

    def _update_info(self):
        from xml.etree import ElementTree as xml
        """Retrieve latest information from the router."""
        _LOGGER.debug('Polling')

        timeout = int(self.scan_interval.total_seconds()/2)
        r = self._request(timeout)
        if 'error_id' in r:
            _LOGGER.error("Can't get connected clients: %s", r['error_msg'])
            return

        self.last_results = []
        #todo
        xml_doc = xml.fromstring(r['text'])
        for host in xml_doc[0].findall('host'):
            if 'up' in host.find('./link').text:
                self.last_results.append(host.find('./mac').text)              
        return
