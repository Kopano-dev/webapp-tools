#!/usr/bin/env python
import kopano
import sys
from MAPI.Util import *

try:
    import json
except ImportError:
    import simplejson as json


def opt_args():
    parser = kopano.parser('skpcf')
    parser.add_option("--user", dest="user", action="store", help="Dump signatures for user")
    return parser.parse_args()


def main():
    options, args = opt_args()
    if not options.user:
        print 'Please use:\n %s --user <username>' % (sys.argv[0])
    else:
        user = kopano.Server(options=options).user(options.user)
        settings = json.loads(user.store.prop(PR_EC_WEBACCESS_SETTINGS_JSON).value)
        if len(settings['settings']['zarafa']['v1']['contexts']['mail']):
            if 'signatures' in settings['settings']['zarafa']['v1']['contexts']['mail']:
                for item in settings['settings']['zarafa']['v1']['contexts']['mail']['signatures']['all']:
                    name = settings['settings']['zarafa']['v1']['contexts']['mail']['signatures']['all'][item]['name']
                    filename = '%s-%s-%s.html' % (user.name, name.replace(' ', '-'), item)
                    print 'Dumping: \'%s\' to \'%s\' ' % (name, filename)
                    with open(filename, 'w') as outfile:
                        outfile.write(settings['settings']['zarafa']['v1']['contexts']['mail']['signatures']['all'][item]['content'].encode('utf-8'))


if __name__ == '__main__':
    main()