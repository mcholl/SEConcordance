import ConfigParser
from datetime import date, datetime, tzinfo, timedelta, time

ini_file = 'seconcord.ini'

def get_last_run(site_name):
    config = ConfigParser.ConfigParser()
    config.read(ini_file)
    if 'last_run' not in config.sections():
        cfg = open(ini_file,'w')
        config.add_section('last_run')
        config.write(cfg)
        cfg.close()
    
    try:
    	lr = config.get('last_run', site_name)
    except ConfigParser.NoOptionError:
    	print "No default set"
        lr= 'Jan 1 1970 12:00'

    return datetime.strptime(lr, "%b %d %Y %H:%M")

def set_last_run(site_name):
    config = ConfigParser.ConfigParser()
    config.read(ini_file)
    
    cfg = open(ini_file,'w')
    last_run = config.set('last_run', site_name, datetime.now().strftime("%b %d %Y %H:%M"))
    config.write(cfg)
    cfg.close()

def get_ini_value(section, key_name):
    config = ConfigParser.ConfigParser()
    config.read(ini_file)
    return config.get(section, key_name)
