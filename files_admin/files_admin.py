#!/usr/bin/env python3
import subprocess
from configobj import ConfigObj
import uuid
from MAPI.Util import *

import kopano

# Try simplejson if json is not available
try:
    import json
except ImportError:
    import simplejson as json


def encode(value):
    output = subprocess.check_output(["php", "deencode.php", "encode", value])
    return output.strip()


def opt_args():
    parser = kopano.parser('skpcfm')
    parser.add_option("--user", dest="user", action="store", help="username")
    parser.add_option("--ssl", dest="ssl", action="store_true", help="Use localhost on port 443")
    parser.add_option("--hostname", dest="hostname", action="store", help="hostname")

    parser.add_option("--file", dest="file", default=[], action="store", help="config file(s) separate by ',' ")
    parser.add_option("--default", dest="default", action="store_true",
                      help="use default user and password in the configfile")

    return parser.parse_args()


def read_settings(user):
    try:
        mapisettings = user.store.prop(PR_EC_WEBACCESS_SETTINGS_JSON).value.decode('utf-8')
        settings = json.loads(mapisettings)
    except Exception as e:
        print('{}: Has no or no valid WebApp settings creating empty config tree'.format(user.name))
        settings = json.loads('{"settings": {"zarafa": {"v1": {"contexts": {"mail": {}}}}}}')
    return settings


def write_settings(user, setting):
    try:
        user.store.create_prop(PR_EC_WEBACCESS_SETTINGS_JSON, setting.encode('utf-8'))
    except Exception as e:
        print('{}: Error Writing WebApp settings for user: {}'.format(e, user.name))


def files(options):
    filesjson = {'accounts': {}}

    files = options.file.split(',')
    for file in files:
        configfile = ConfigObj(file)
        if configfile['setting']['use_zarafa_credentials']:
            username = configfile['setting']['default_user']
        else:
            username = options.user
        password = encode(configfile['setting']['default_password'])
        backendoptions = {
            'ftp': {"backend_features": {
                "Streaming": "true", }},
            'webdav': {"backend_features": {
                "Quota": "true",
                "VersionInfo": "true"}},
            'owncloud': {"backend_features": {
                "Quota": "true",
                "Sharing": "true",
                "VersionInfo": "true"}},
            'smb': {"backend_features": {
                "Quota": "true",
                "Streaming": "true",
                "VersionInfo": "true"}},
        }

        if file == 'seafile.cfg':
            password = encode(options.user)
            username = kopano.Server(options).user(options.user).email

        if 'local' in file:
            if options.ssl:
                port = '443'
                address = options.hostname
                ssl = 'true'
            else:
                port = configfile['setting']['server_port']
                address = configfile['setting']['server_address']
                ssl = configfile['setting']['server_ssl']
        else:
            port = configfile['setting']['server_port']
            address = configfile['setting']['server_address']
            ssl = configfile['setting']['server_ssl']
        id = str(uuid.uuid4())
        filesjson['accounts'][id] = {
            "status": "ok",
            "backend_config": {
                "server_path": encode(configfile['setting']['server_path']).decode('utf-8'),
                "workgroup": encode(configfile['setting']['workgroup']).decode('utf-8'),
                "server_address": encode(address).decode('utf-8'),
                "server_ssl": ssl,
                "current_account_id": encode('d4cacda458a2a26c301f2b7d75ada530').decode('utf-8'),
                "use_zarafa_credentials": configfile['setting']['use_zarafa_credentials'],
                "user": encode(username).decode('utf-8'),
                "password": password.decode('utf-8'),
                "server_port": encode(port).decode('utf-8')
            },
            "cannot_change": False,
            "name": configfile['setting']['name'],
            "status_description": "Account is ready to use.",
            "id": id,
            "backend_features": backendoptions[configfile['setting']['type'].lower()]['backend_features'],
            "backend": configfile['setting']['type']
        }

        if configfile['setting']['type'].lower() == 'ftp':
            filesjson['accounts'][id]['backend_config']['server_pasv'] = configfile['setting']['server_pasv']

    return filesjson


def main():
    options, args = opt_args()

    server = kopano.Server(options)
    user = server.user(options.user)
    webappsettings = read_settings(user)
    if not webappsettings['settings']['zarafa']['v1'].get('plugins'):
        webappsettings['settings']['zarafa']['v1']['plugins'] = {}
    webappsettings['settings']['zarafa']['v1']['plugins']['files'] = files(options)
    write_settings(user, json.dumps(webappsettings))


if __name__ == '__main__':
    main()
