#!/usr/bin/env python
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
    proc = subprocess.Popen(["php", "deencode.php", "encode", value], stdout=subprocess.PIPE)
    return proc.communicate()[0]


def opt_args():
    parser = kopano.parser('skpcfmUP')
    parser.add_option("--user", dest="user", action="store", help="username")
    parser.add_option("--file", dest="file", default=[], action="store", help="config file(s) separate by ',' ")
    parser.add_option("--overwrite", dest="overwrite", action="store_true", help="overwrite files settings")
    parser.add_option("--default", dest="default", action="store_true",
                      help="use default user and password in the configfile")

    return parser.parse_args()


def read_settings(options):

    try:
        user = kopano.Server(options).user(options.user)
    except MAPIErrorLogonFailed as e:
        print('User \'{}\' not found ({})'.format(options.user, e))
        sys.exit(1)

    if not user.store:
        print('User \'{}\' has no user store ({})'.format(options.user, e))
        sys.exit(1)

    try:
        mapisettings = user.store.prop(PR_EC_WEBACCESS_SETTINGS_JSON).value
        return mapisettings
    except Exception:
        print('{}: Has no or no valid WebApp settings creating empty config tree'.format(user.name))
        return '{"settings": {"zarafa": {"v1": {"contexts": {"mail": {}}}}}}'


def write_settings(data, options):
    user = kopano.Server(options).user(options.user)
    user.store.create_prop(PR_EC_WEBACCESS_SETTINGS_JSON, data.encode('utf-8'))
    print('Writing settings for user \'{}\''.format(user.fullname))


def files(options):
    filesjson = '{'
    if options.overwrite:
        filesjson = '{"accounts": {'
    num = 0
    files = options.file.split(',')
    for file in files:
        configfile = ConfigObj(file)
        if options.default:
            username = configfile['setting']['default_user']
        else:
            username = options.user
        if num != 0:
            filesjson += ','
        id = uuid.uuid4()
        filesjson += '''
            "%s": {
                "status": "ok",
                "backend_config": {
                    "server_path": "%s",
                    "workgroup": "%s",
                    "server_address": "%s",
                    "server_ssl": %s,
                    "current_account_id": "%s",
                    "use_zarafa_credentials": %s,
                    "user": "%s",
                    "password": "%s",
                    "server_port": "%s"
                },
		"cannot_change": false,
                "name": "%s",
                "status_description": "Account is ready to use.",
                "id": "%s",
                "backend_features": {
                    "Sharing": true,
                    "VersionInfo": true,
                    "Quota": true
                },
                "backend": "%s"
            }''' % (id, encode(configfile['setting']['server_path']), encode(configfile['setting']['workgroup']),
                    encode(configfile['setting']['server_address']), configfile['setting']['server_ssl'],
                    encode('d4cacda458a2a26c301f2b7d75ada530'), configfile['setting']['use_zarafa_credentials'],
                    encode(username), encode(configfile['setting']['default_password']),
                    encode(configfile['setting']['server_port']), configfile['setting']['name'], id, configfile['setting']['type'])
        num += 1
    if options.overwrite:
        filesjson += '}}'
    else:
        filesjson += '}'
    return filesjson


def main():
    options, args = opt_args()

    data = read_settings(options)
    webappsettings = json.loads(data)

    if not webappsettings['settings']['zarafa']['v1'].get('plugins'):
        webappsettings['settings']['zarafa']['v1']['plugins'] = {}

    if options.overwrite:
        webappsettings['settings']['zarafa']['v1']['plugins']['files'] = json.loads(files(options))
    else:
        if not webappsettings['settings']['zarafa']['v1']['plugins'].get('files'):
            webappsettings['settings']['zarafa']['v1']['plugins']['files'] = {}
        if not webappsettings['settings']['zarafa']['v1']['plugins']['files'].get('accounts'):
            webappsettings['settings']['zarafa']['v1']['plugins']['files']['accounts'] = {}
        webappsettings['settings']['zarafa']['v1']['plugins']['files']['accounts'].update(json.loads(files(options)))

    write_settings(json.dumps(webappsettings), options)


if __name__ == '__main__':
    main()


