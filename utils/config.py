import os
import configparser

#Loads a configuration file. If one does not exist under the name\
# 'config.ini', one will be created.
def load_config():
    config = configparser.ConfigParser();

    if os.path.exists('config.ini') is False:
        config['DEFAULT'] = {}
        config['MARIADB'] = {
                'Host': '0.0.0.0',
                'Port': '3066',
                'Username': 'johndoe',
                'Password': 'password',
                'Database': 'civil_servant_dev',
                'ConnectionPoolName': 'CivilServantMariaDBConnectionPool',
                'ConnectionPoolSize': 5
                }
        config['CIVILSERVANT'] = {
                'CommandPrefix': '?',
                'Owner': 'owner-id'
                }

        with open('config.ini', 'w') as file:
            config.write(file)
    config.read('config.ini')
    return config
