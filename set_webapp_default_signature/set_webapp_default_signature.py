#!/usr/bin/env python
# coding=utf-8
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
"""
Set A Default WebApp Signature.
"""
import json
import kopano
from MAPI.Tags import *


def read_settings(user):
    try:
        mapisettings = user.store.prop(PR_EC_WEBACCESS_SETTINGS_JSON).value
        settings = json.loads(mapisettings)
    except Exception as e:
        print '%s: Has no or no valid WebApp settings creating empty config tree' % user.name
        settings = json.loads(
            '{"settings": {"zarafa": {"v1": {"contexts": {"mail": {}}}}}}')
    return settings


def write_settings(user, webappsettings):
    try:
        user.store.create_prop(PR_EC_WEBACCESS_SETTINGS_JSON, webappsettings)
    except Exception as e:
        print '%s: Error Writing WebApp settings for user: %s' % (e, user.name)


def main(options):
    with open(options.file, 'r') as sigfile:
        signaturehtml = sigfile.read()
        signatureid = '1'
        signaturename = options.file.replace('template', 'default').replace('-', ' ').replace('.html', '').title().split('/')[-1].replace(' Nl', ' NL').replace(
            ' De', ' DE')
        signaturecontent = dict(
            {u'name': signaturename, u'content': signaturehtml, u'isHTML': True})
        runusers = []
        if options.allusers:
            for ruser in server.users(remote=False):
                runusers.append(ruser.name)
        else:
            runusers = options.users

        for username in runusers:
            try:
                user = server.user(username)
                webappsettings = read_settings(user)
            except Exception as e:
                print e
                continue

            if not len(webappsettings['settings']['zarafa']['v1']['contexts']['mail']):
                print "%s: Adding config tree." % user.name
                webappsettings['settings']['zarafa'][
                    'v1']['contexts']['mail'] = dict({})
            if 'signatures' not in list(webappsettings['settings']['zarafa']['v1']['contexts']['mail']):
                print "%s: Adding Signature settings to config tree." % user.name
                webappsettings['settings']['zarafa']['v1'][
                    'contexts']['mail']['signatures'] = dict({})
            if 'all' not in list(webappsettings['settings']['zarafa']['v1']['contexts']['mail']['signatures']):
                print "%s: Empty Signature settings detected." % user.name
                webappsettings['settings']['zarafa']['v1']['contexts'][
                    'mail']['signatures'] = dict({'all': dict({})})
            print '%s: Adding/Replacing Default Signature with %s' % (user.name, signaturename)
            webappsettings['settings']['zarafa']['v1']['contexts']['mail']['signatures']['all'][
                signatureid] = signaturecontent
            webappsettings['settings']['zarafa']['v1']['contexts'][
                'mail']['signatures']['new_message'] = signatureid
            webappsettings['settings']['zarafa']['v1']['contexts']['mail']['signatures'][
                'replyforward_message'] = signatureid
            write_settings(user, json.dumps(webappsettings))


if __name__ == '__main__':
    parser = kopano.parser('uUPckpsC')  # select common cmd-line options
    parser.add_option('-a', dest='allusers', action='store_true',
                      default=None, help='run program for all local users')
    parser.add_option('-f', dest='file', action='store',
                      default=None, help='signature filename')
    options, args = parser.parse_args()
    server = kopano.Server(options=options)
    if (options.users or options.allusers) and options.file:
        main(options)
