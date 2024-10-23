import weewx
from weewx.engine import StdService
import serial
import syslog
import weewx.units

weewx.units.obs_group_dict['victronBatteryVoltage'] = 'group_volt'
weewx.units.obs_group_dict['victronCurrent'] = 'group_amps'
weewx.units.obs_group_dict['victronPanelVoltage'] = 'group_volt'
weewx.units.obs_group_dict['victronPanelPower'] = 'group_watts'

weewx.units.USUnits['group_amps'] = 'amps'
weewx.units.MetricUnits['group_amps'] = 'amps'
weewx.units.MetricWXUnits['group_amps'] = 'amps'
weewx.units.default_unit_format_dict['amps'] = '%.2f'
weewx.units.default_unit_label_dict['amps'] = ' A'

weewx.units.USUnits['group_watts'] = 'watts'
weewx.units.MetricUnits['group_watts'] = 'watts'
weewx.units.MetricWXUnits['group_watts'] = 'watts'
weewx.units.default_unit_format_dict['watts'] = '%.0f'
weewx.units.default_unit_label_dict['watts'] = ' W'

try:
    # Test for new-style weewx v4 logging by trying to import weeutil.logger
    import weeutil.logger
    import logging

    log = logging.getLogger(__name__)

    def logdbg(msg):
        log.debug(msg)

    def loginf(msg):
        log.info(msg)

    def logerr(msg):
        log.error(msg)

except ImportError:
    # Old-style weewx logging
    import syslog

    def logmsg(level, msg):
        syslog.syslog(level, 'Belchertown Extension: %s' % msg)

    def logdbg(msg):
        logmsg(syslog.LOG_DEBUG, msg)

    def loginf(msg):
        logmsg(syslog.LOG_INFO, msg)

    def logerr(msg):
        logmsg(syslog.LOG_ERR, msg)
    

logdbg("victron.py loading...")


def get_victron_voltage(port):
    with serial.Serial(port, 19200, timeout=1) as ser:
        voltage = ''
        while voltage == '':
            line = ser.readline()
            x = line.split()
            if 'V' in x:
		try:
               	    voltage = float(x[1])/1000.0
		except:
                    pass
    return voltage
 
def get_victron_current(port):
    with serial.Serial(port, 19200, timeout=1) as ser:
        current = ''
        while current == '':
            line = ser.readline()
            x = line.split()
            if 'I' in x:
		try:
                    current = float(x[1])/1000.0
		except:
                    pass
    return current

def get_victron_panel_voltage(port):
    with serial.Serial(port, 19200, timeout=1) as ser:
        voltage = ''
        while voltage == '':
            line = ser.readline()
            x = line.split()
            if 'VPV' in x:
		try:
                    voltage = float(x[1])/1000.0
		except:
                    pass
    return voltage

def get_victron_panel_power(port):
    with serial.Serial(port, 19200, timeout=1) as ser:
        power = ''
        while power == '':
            line = ser.readline()
            x = line.split()
            if 'PPV' in x:
                power = x[1]
    return power

def get_victron_controller_state(port):
    with serial.Serial(port, 19200, timeout=1) as ser:
        cs = ''
        while cs == '':
            line = ser.readline()
            x = line.split()
            if 'CS' in x:
                cs = x[1]
    return cs

class AddVictronInfo(StdService):
    def __init__(self, engine, config_dict):

        # Initialize my superclass first:
        super(AddVictronInfo, self).__init__(engine, config_dict)

        # Bind to any new archive record events:
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)

    def new_archive_record(self, event):
#        port = '/dev/ttyUSB1'
        port = '/dev/victronUSB'
        house_battery_voltage = get_victron_voltage(port)
        event.record['victronBatteryVoltage'] = house_battery_voltage
        current = get_victron_current(port)
        event.record['victronCurrent'] = current
        event.record['victronPanelVoltage'] = get_victron_panel_voltage(port)
        event.record['victronPanelPower'] = get_victron_panel_power(port)
        event.record['victronControllerState'] = get_victron_controller_state(port)


import schemas.wview_extended

schema_with_victron = {
    'table': schemas.wview_extended.table + [('victronBatteryVoltage', 'REAL'),('victronCurrent', 'REAL'),('victronPanelVoltage', 'REAL'), ('victronPanelPower', 'REAL'), ('victronControllerState', 'REAL'), ('lowerTankLevel', 'REAL')],
    'day_summaries' : schemas.wview_extended.day_summaries + [('victronBatteryVoltage', 'SCALAR'),('victronCurrent', 'SCALAR'),('victronPanelVoltage', 'SCALAR'),('victronPanelPower', 'SCALAR'),('victronControllerState','SCALAR'), ('lowerTankLevel','SCALAR')]
}

