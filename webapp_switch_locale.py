#!/usr/bin/env python
# encoding: utf-8
import json
import kopano
from MAPI.Util import *
import sys


def opt_args():
    parser = kopano.parser('skpcfm')
    parser.add_option("--user", dest="user", action="store", help="Run script for user")
    parser.add_option("--locale", dest="locale", action="store", help="Set new locale")
    return parser.parse_args()


def main():
    options, args = opt_args()

    if not options.user:
        print 'Please use:\n %s --user <username> [--locale]' % (sys.argv[0])
        sys.exit()

    user = kopano.Server(options).user(options.user)
    settings = json.loads(user.store.prop(PR_EC_WEBACCESS_SETTINGS_JSON).value)
    current = settings['settings']['zarafa']['v1']['main']['language']
    print 'Original locale: %s' % current

    if options.locale:
        print 'Setting locale to: %s' % options.locale
        settings['settings']['zarafa']['v1']['main']['language'] = options.locale
        user.store.prop(PR_EC_WEBACCESS_SETTINGS_JSON).set_value(json.dumps(settings))


if __name__ == "__main__":
    main()
