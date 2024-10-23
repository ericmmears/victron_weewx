import weewx
from weewx.engine import StdService
import syslog
import weewx.units

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
    

logdbg("tank_level.py loading...")


def get_lower_tank_level():
    file = open("/var/www/html/weewx/tank/lower_tank_level.log", "r")
    lower_tank_level = 0.0;
    for line in file:
        if 'tank_level' in line:
            line_split = line.split(' ')
            lower_tank_level = line_split[2] 
    file.close()
    return lower_tank_level
 
class AddTankInfo(StdService):
    def __init__(self, engine, config_dict):

        # Initialize my superclass first:
        super(AddTankInfo, self).__init__(engine, config_dict)

        # Bind to any new archive record events:
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)

    def new_archive_record(self, event):
        lower_tank_level = get_lower_tank_level()
        logdbg("logging lower_tank_level=" + str(lower_tank_level))
        event.record['lowerTankLevel'] = lower_tank_level


import schemas.wview_extended

schema_with_victron = {
    'table': schemas.wview_extended.table + [('victronBatteryVoltage', 'REAL'),('victronCurrent', 'REAL'),('victronPanelVoltage', 'REAL'), ('victronPanelPower', 'REAL'), ('victronControllerState', 'REAL'), ('lowerTankLevel', 'REAL')],
    'day_summaries' : schemas.wview_extended.day_summaries + [('victronBatteryVoltage', 'SCALAR'),('victronCurrent', 'SCALAR'),('victronPanelVoltage', 'SCALAR'),('victronPanelPower', 'SCALAR'),('victronControllerState','SCALAR'), ('lowerTankLevel','SCALAR')]
}

