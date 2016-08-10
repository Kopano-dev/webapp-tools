#!/usr/bin/env python
#encoding: utf-8

from MAPI import *
from MAPI.Util import *
import sys
import kopano

try:
        import json
except ImportError:
        import simplejson as json

def opt_args():
    parser = kopano.parser('skpcfm')
    parser.add_option("--user", dest="user", action="store", help="Run script for user")
    parser.add_option("--backup", dest="backup", action="store_true", help="Backup webapp setting ")
    parser.add_option("--restore", dest="restore", action="store_true", help="Restore webapp settings")

    return parser.parse_args()


def main():
    options, args = opt_args()

    if not options.user or (not options.backup and not options.restore):
        print 'Please use:\n %s --user <username> (--backup or --restore)  ' % (sys.argv[0])
        sys.exit()

    user = kopano.Server(options).user(options.user)
    if options.backup:
        webapp = json.loads(user.store.prop(PR_EC_WEBACCESS_SETTINGS_JSON).value)
        f = open('%s.json' % user.name,'w')

        f.write(json.dumps(webapp, sort_keys=True,
                     indent=4, separators=(',', ': ')))
        f.close()
    if options.restore:
        with open('%s.json' % user.name) as data_file:
            data = json.load(data_file)

        print data
        user.store.prop(PR_EC_WEBACCESS_SETTINGS_JSON).set_value(json.dumps(data))
        
        
if __name__ == "__main__":
    main()