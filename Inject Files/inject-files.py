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

# Define where to read and write our WebApp config from / to
PR_EC_WEBACCESS_SETTINGS_JSON = PROP_TAG(PT_STRING8, PR_EC_BASE + 0x72)


def encode(value):
    proc = subprocess.Popen(["php", "deencode.php", "encode", value], stdout=subprocess.PIPE)
    return proc.communicate()[0]


def opt_args():
    parser = kopano.parser('skpcfm')
    parser.add_option("--user", dest="user", action="store", help="username")
    parser.add_option("--file", dest="file", default=[], action="store", help="config file(s) separate by ',' ")
    parser.add_option("--default", dest="default", action="store_true",
                      help="use default user and password in the configfile")

    return parser.parse_args()


def read_settings(options):
    data = None

    try:
        user = kopano.Server(options).user(options.user)

        st = user.store.mapiobj

    except MAPIErrorNotFound as e:
        print 'User \'%s\' has no user store (%s)' % (options.user, e)
        return

    except MAPIErrorLogonFailed as e:
        print 'User \'%s\' not found (%s)' % (options.user, e)
        return

    try:
        settings = st.OpenProperty(PR_EC_WEBACCESS_SETTINGS_JSON, IID_IStream, 0, 0)
        data = settings.Read(33554432)
    except Exception as e:
        print 'No WebApp settings found.'
        data = '{"settings": {"zarafa": {"v1": {"contexts": {"mail": {}}}}}}'

    return data


def write_settings(data, options):
    user = kopano.Server(options).user(options.user)
    st = user.store.mapiobj

    settings = st.OpenProperty(PR_EC_WEBACCESS_SETTINGS_JSON, IID_IStream, 0, MAPI_MODIFY | MAPI_CREATE)
    settings.SetSize(0)
    settings.Seek(0, STREAM_SEEK_END)

    writesettings = settings.Write(data)

    if writesettings:
        print 'Writing settings for user \'%s\'' % user.fullname
        settings.Commit(0)
    else:
        print 'Writing settings for user \'%s\' failed.' % user.fullname


def files(options):
    filesjson = '''{
        "accounts": {'''
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

    filesjson += '''
        }
    }
    '''
    return filesjson


def main():
    options, args = opt_args()

    data = read_settings(options)
    webappsettings = json.loads(data)

    try:
        if webappsettings['settings']['zarafa']['v1']['plugins']:
            pass
    except:
        webappsettings['settings']['zarafa']['v1']['plugins'] = dict({})

    webappsettings['settings']['zarafa']['v1']['plugins']['files'] = json.loads(files(options))
    write_settings(json.dumps(webappsettings), options)


if __name__ == '__main__':
    main()
