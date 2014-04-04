import ConfigParser
from datetime import date, datetime, tzinfo, timedelta, time

class Ini:

    def __init__(self, inifile):
        self.ini_file = inifile

    def get_last_run(self, site_name):
        config = ConfigParser.ConfigParser()
        config.read(self.ini_file)
        if 'last_run' not in config.sections():
            cfg = open(ini_file,'w')
            config.add_section('last_run')
            config.write(cfg)
            cfg.close()
        
        lr= 'Jan 1 1970 12:00'
        try:
        	lr = config.get('last_run', site_name)
        except ConfigParser.NoOptionError:
        	print "No default set"

        return datetime.strptime(lr, "%b %d %Y %H:%M")

    def set_last_run(self, site_name):
        config = ConfigParser.ConfigParser()
        config.read(ini_file)
        
        cfg = open(ini_file,'w')
        last_run = config.set('last_run', site_name, datetime.now().strftime("%b %d %Y %H:%M"))
        config.write(cfg)
        cfg.close()

    def get_ini_value(self, section, key_name):
        config = ConfigParser.ConfigParser()
        config.read(self.ini_file)
        return config.get(section, key_name)

    def report_last_runs(self):
        config = ConfigParser.ConfigParser()
        config.read(self.ini_file)
        if 'last_run' not in config.sections():
            return {'error': 'No [last_run] section defined'}

        return config.items('last_run')


