# -*- coding: utf-8 -*-
'''
Module for managing timezone on Windows systems.
'''
from __future__ import absolute_import, unicode_literals, print_function

# Import Python libs
import logging
import pytz
from datetime import datetime

# Import Salt libs
from salt.exceptions import CommandExecutionError
import salt.utils.path
import salt.utils.platform
import salt.utils.win_reg

log = logging.getLogger(__name__)

# Define the module's virtual name
__virtualname__ = 'timezone'


class TzMapper(object):
    def __init__(self, unix_to_win):
        self.win_to_unix = {k.lower(): v for k, v in unix_to_win.items()}
        self.unix_to_win = {v.lower(): k for k, v in unix_to_win.items()}

    def add(self, k, v):
        self.unix_to_win[k.lower()] = v
        self.win_to_unix[v.lower()] = k

    def remove(self, k):
        self.win_to_unix.pop(self.unix_to_win.pop(k.lower()).lower())

    def get_win(self, key, default=None):
        return self.unix_to_win.get(key.lower(), default)

    def get_unix(self, key, default=None):
        return self.win_to_unix.get(key.lower(), default)


mapper = TzMapper({
    'AUS Central Standard Time': 'Australia/Darwin',
    'AUS Eastern Standard Time': 'Australia/Sydney',
    'Afghanistan Standard Time': 'Asia/Kabul',
    'Alaskan Standard Time': 'America/Anchorage',
    'Aleutian Standard Time': 'America/Adak',
    'Altai Standard Time': 'Asia/Barnaul',
    'Arab Standard Time': 'Asia/Riyadh',
    'Arabian Standard Time': 'Asia/Dubai',
    'Arabic Standard Time': 'Asia/Baghdad',
    'Argentina Standard Time': 'America/Buenos_Aires',
    'Astrakhan Standard Time': 'Europe/Astrakhan',
    'Atlantic Standard Time': 'America/Halifax',
    'Aus Central W. Standard Time': 'Australia/Eucla',
    'Azerbaijan Standard Time': 'Asia/Baku',
    'Azores Standard Time': 'Atlantic/Azores',
    'Bahia Standard Time': 'America/Bahia',
    'Bangladesh Standard Time': 'Asia/Dhaka',
    'Belarus Standard Time': 'Europe/Minsk',
    'Bougainville Standard Time': 'Pacific/Bougainville',
    'Canada Central Standard Time': 'America/Regina',
    'Cape Verde Standard Time': 'Atlantic/Cape_Verde',
    'Caucasus Standard Time': 'Asia/Yerevan',
    'Cen. Australia Standard Time': 'Australia/Adelaide',
    'Central America Standard Time': 'America/Guatemala',
    'Central Asia Standard Time': 'Asia/Almaty',
    'Central Brazilian Standard Time': 'America/Cuiaba',
    'Central Europe Standard Time': 'Europe/Budapest',
    'Central European Standard Time': 'Europe/Warsaw',
    'Central Pacific Standard Time': 'Pacific/Guadalcanal',
    'Central Standard Time': 'America/Chicago',
    'Central Standard Time (Mexico)': 'America/Mexico_City',
    'Chatham Islands Standard Time': 'Pacific/Chatham',
    'China Standard Time': 'Asia/Shanghai',
    'Cuba Standard Time': 'America/Havana',
    'Dateline Standard Time': 'Etc/GMT+12',
    'E. Africa Standard Time': 'Africa/Nairobi',
    'E. Australia Standard Time': 'Australia/Brisbane',
    'E. Europe Standard Time': 'Europe/Chisinau',
    'E. South America Standard Time': 'America/Sao_Paulo',
    'Easter Island Standard Time': 'Pacific/Easter',
    'Eastern Standard Time': 'America/New_York',
    'Eastern Standard Time (Mexico)': 'America/Cancun',
    'Egypt Standard Time': 'Africa/Cairo',
    'Ekaterinburg Standard Time': 'Asia/Yekaterinburg',
    'FLE Standard Time': 'Europe/Kiev',
    'Fiji Standard Time': 'Pacific/Fiji',
    'GMT Standard Time': 'Europe/London',
    'GTB Standard Time': 'Europe/Bucharest',
    'Georgian Standard Time': 'Asia/Tbilisi',
    'Greenland Standard Time': 'America/Godthab',
    'Greenwich Standard Time': 'Atlantic/Reykjavik',
    'Haiti Standard Time': 'America/Port-au-Prince',
    'Hawaiian Standard Time': 'Pacific/Honolulu',
    'India Standard Time': 'Asia/Calcutta',
    'Iran Standard Time': 'Asia/Tehran',
    'Israel Standard Time': 'Asia/Jerusalem',
    'Jordan Standard Time': 'Asia/Amman',
    'Kaliningrad Standard Time': 'Europe/Kaliningrad',
    'Korea Standard Time': 'Asia/Seoul',
    'Libya Standard Time': 'Africa/Tripoli',
    'Line Islands Standard Time': 'Pacific/Kiritimati',
    'Lord Howe Standard Time': 'Australia/Lord_Howe',
    'Magadan Standard Time': 'Asia/Magadan',
    'Magallanes Standard Time': 'America/Punta_Arenas',
    'Marquesas Standard Time': 'Pacific/Marquesas',
    'Mauritius Standard Time': 'Indian/Mauritius',
    'Middle East Standard Time': 'Asia/Beirut',
    'Montevideo Standard Time': 'America/Montevideo',
    'Morocco Standard Time': 'Africa/Casablanca',
    'Mountain Standard Time': 'America/Denver',
    'Mountain Standard Time (Mexico)': 'America/Chihuahua',
    'Myanmar Standard Time': 'Asia/Rangoon',
    'N. Central Asia Standard Time': 'Asia/Novosibirsk',
    'Namibia Standard Time': 'Africa/Windhoek',
    'Nepal Standard Time': 'Asia/Katmandu',
    'New Zealand Standard Time': 'Pacific/Auckland',
    'Newfoundland Standard Time': 'America/St_Johns',
    'Norfolk Standard Time': 'Pacific/Norfolk',
    'North Asia East Standard Time': 'Asia/Irkutsk',
    'North Asia Standard Time': 'Asia/Krasnoyarsk',
    'North Korea Standard Time': 'Asia/Pyongyang',
    'Omsk Standard Time': 'Asia/Omsk',
    'Pacific SA Standard Time': 'America/Santiago',
    'Pacific Standard Time': 'America/Los_Angeles',
    'Pacific Standard Time (Mexico)': 'America/Tijuana',
    'Pakistan Standard Time': 'Asia/Karachi',
    'Paraguay Standard Time': 'America/Asuncion',
    'Romance Standard Time': 'Europe/Paris',
    'Russia Time Zone 10': 'Asia/Srednekolymsk',
    'Russia Time Zone 11': 'Asia/Kamchatka',
    'Russia Time Zone 3': 'Europe/Samara',
    'Russian Standard Time': 'Europe/Moscow',
    'SA Eastern Standard Time': 'America/Cayenne',
    'SA Pacific Standard Time': 'America/Bogota',
    'SA Western Standard Time': 'America/La_Paz',
    'SE Asia Standard Time': 'Asia/Bangkok',
    'Saint Pierre Standard Time': 'America/Miquelon',
    'Sakhalin Standard Time': 'Asia/Sakhalin',
    'Samoa Standard Time': 'Pacific/Apia',
    'Saratov Standard Time': 'Europe/Saratov',
    'Singapore Standard Time': 'Asia/Singapore',
    'South Africa Standard Time': 'Africa/Johannesburg',
    'Sri Lanka Standard Time': 'Asia/Colombo',
    'Syria Standard Time': 'Asia/Damascus',
    'Taipei Standard Time': 'Asia/Taipei',
    'Tasmania Standard Time': 'Australia/Hobart',
    'Tocantins Standard Time': 'America/Araguaina',
    'Tokyo Standard Time': 'Asia/Tokyo',
    'Tomsk Standard Time': 'Asia/Tomsk',
    'Tonga Standard Time': 'Pacific/Tongatapu',
    'Transbaikal Standard Time': 'Asia/Chita',
    'Turkey Standard Time': 'Europe/Istanbul',
    'Turks And Caicos Standard Time': 'America/Grand_Turk',
    'US Eastern Standard Time': 'America/Indianapolis',
    'US Mountain Standard Time': 'America/Phoenix',
    'UTC': 'Etc/GMT',
    'UTC+12': 'Etc/GMT-12',
    'UTC+13': 'Etc/GMT-13',
    'UTC-02': 'Etc/GMT+2',
    'UTC-08': 'Etc/GMT+8',
    'UTC-09': 'Etc/GMT+9',
    'UTC-11': 'Etc/GMT+11',
    'Ulaanbaatar Standard Time': 'Asia/Ulaanbaatar',
    'Venezuela Standard Time': 'America/Caracas',
    'Vladivostok Standard Time': 'Asia/Vladivostok',
    'W. Australia Standard Time': 'Australia/Perth',
    'W. Central Africa Standard Time': 'Africa/Lagos',
    'W. Europe Standard Time': 'Europe/Berlin',
    'W. Mongolia Standard Time': 'Asia/Hovd',
    'West Asia Standard Time': 'Asia/Tashkent',
    'West Bank Standard Time': 'Asia/Hebron',
    'West Pacific Standard Time': 'Pacific/Port_Moresby',
    'Yakutsk Standard Time': 'Asia/Yakutsk'})


def __virtual__():
    '''
    Only load on windows
    '''
    if salt.utils.platform.is_windows() and salt.utils.path.which('tzutil'):
        return __virtualname__
    return (False, "Module win_timezone: tzutil not found or is not on Windows client")


def get_zone():
    '''
    Get current timezone (i.e. America/Denver)

    Returns:
        str: Timezone in unix format

    CLI Example:

    .. code-block:: bash

        salt '*' timezone.get_zone
    '''
    win_zone = salt.utils.win_reg.read_value(
        hive='HKLM',
        key='SYSTEM\\CurrentControlSet\\Control\\TimeZoneInformation',
        vname='TimeZoneKeyName')['vdata']
    return mapper.get_unix(win_zone.lower(), 'Unknown')


def get_offset():
    '''
    Get current numeric timezone offset from UTC (i.e. -0700)

    Returns:
        str: Offset from UTC

    CLI Example:

    .. code-block:: bash

        salt '*' timezone.get_offset
    '''
    # http://craigglennie.com/programming/python/2013/07/21/working-with-timezones-using-Python-and-pytz-localize-vs-normalize/
    tz_object = pytz.timezone(get_zone())
    utc_time = pytz.utc.localize(datetime.today())
    loc_time = utc_time.astimezone(tz_object)
    norm_time = tz_object.normalize(loc_time)
    time_zone = norm_time.astimezone(tz_object)
    return time_zone.utcoffset().total_seconds() / 3600


def get_zonecode():
    '''
    Get current timezone (i.e. PST, MDT, etc)

    Returns:
        str: An abbreviated timezone code

    CLI Example:

    .. code-block:: bash

        salt '*' timezone.get_zonecode
    '''
    tz_object = pytz.timezone(get_zone())
    loc_time = tz_object.localize(datetime.today())
    return loc_time.tzname()


def set_zone(timezone):
    '''
    Sets the timezone using the tzutil.

    Args:
        timezone (str): A valid timezone

    Returns:
        bool: ``True`` if successful, otherwise ``False``

    Raises:
        CommandExecutionError: If invalid timezone is passed

    CLI Example:

    .. code-block:: bash

        salt '*' timezone.set_zone 'America/Denver'
    '''
    # if it's one of the key's just use it
    if timezone.lower() in mapper.win_to_unix:
        win_zone = timezone

    elif timezone.lower() in mapper.unix_to_win:
        # if it's one of the values, use the key
        win_zone = mapper.get_win(timezone)

    else:
        # Raise error because it's neither key nor value
        raise CommandExecutionError('Invalid timezone passed: {0}'.format(timezone))

    # Set the value
    cmd = ['tzutil', '/s', win_zone]
    __salt__['cmd.run'](cmd, python_shell=False)
    return zone_compare(timezone)


def zone_compare(timezone):
    '''
    Compares the given timezone with the machine timezone. Mostly useful for
    running state checks.

    Args:
        timezone (str): The timezone to compare

    Returns:
        bool: ``True`` if they match, otherwise ``False``

    Example:

    .. code-block:: bash

        salt '*' timezone.zone_compare 'America/Denver'
    '''
    # if it's one of the key's just use it
    if timezone.lower() in mapper.win_to_unix:
        check_zone = timezone

    elif timezone.lower() in mapper.unix_to_win:
        # if it's one of the values, use the key
        check_zone = mapper.get_win(timezone)

    else:
        # Raise error because it's neither key nor value
        raise CommandExecutionError('Invalid timezone passed: {0}'
                                    ''.format(timezone))

    return get_zone() == mapper.get_unix(check_zone, 'Unknown')


def get_hwclock():
    '''
    Get current hardware clock setting (UTC or localtime)

    .. note::
        The hardware clock is always local time on Windows so this will always
        return "localtime"

    CLI Example:

    .. code-block:: bash

        salt '*' timezone.get_hwclock
    '''
    # The hardware clock is always localtime on Windows
    return 'localtime'


def set_hwclock(clock):
    '''
    Sets the hardware clock to be either UTC or localtime

    .. note::
        The hardware clock is always local time on Windows so this will always
        return ``False``

    CLI Example:

    .. code-block:: bash

        salt '*' timezone.set_hwclock UTC
    '''
    # The hardware clock is always localtime on Windows
    return False
