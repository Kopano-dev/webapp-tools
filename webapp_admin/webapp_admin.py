#!/usr/bin/env python3
# encoding: utf-8
import sys
try:
    import kopano
except ImportError:
    print('python-kopano should be installed on your system')
    sys.exit(1)
try:
    from MAPI.Util import *
except ImportError:
    print('python-mapi should be installed on your system')
    sys.exit(1)
import json
import base64
try:
    import OpenSSL.crypto
except ImportError:
    print('pip3 install pyOpenSSL')
    sys.exit(1)
from datetime import datetime
from time import mktime
import getpass
import time
from optparse import OptionGroup
try:
    from dotty_dict import dotty
except ImportError:
    print('dotty_dict not found on your system. Run pip3 install dotty_dict')


"""
Read user settings

:param print_help: Print help
:return: Parser arguments
"""
def opt_args(print_help=None):

    # Define the kopano parser
    parser = kopano.parser('skpcufmUP')

    # Common option group
    group = OptionGroup(parser, "Common", "")
    group.add_option("--all-users", dest="all_users", action="store_true", help="Run for all users")
    group.add_option("--location", dest="location", action="store", help="Change location where scripts saves the files")
    group.add_option("--file", dest="file", action="store", help="Use specific file")
    group.add_option("--backup", dest="backup", action="store_true", help="Backup Webapp settings")
    group.add_option("--restore", dest="restore", action="store_true", help="Restore Webapp settings")
    group.add_option("--reset", dest="reset", action="store_true", help="Reset WebApp settings")
    parser.add_option_group(group)

    # Signature option group
    group = OptionGroup(parser, "Signature", "")
    group.add_option("--backup-signature", dest="backup_signature", action="store_true", help="Backup signature")
    group.add_option("--restore-signature", dest="restore_signature", action="store", help="Restore signature (need file name)")
    group.add_option("--replace", dest="replace", action="store_true", help="Replace existing signature, file layout must be: username_signature-name_signatureid.html")
    group.add_option("--default-signature", dest="default_signature", action="store_true", help="Set signature as default one")
    parser.add_option_group(group)

    # S/MIME option group
    group = OptionGroup(parser, "S/MIME", "")
    group.add_option("--export-smime", dest="export_smime", action="store_true", help="Export private S/MIME certificate")
    group.add_option("--import-smime", dest="import_smime", action="store", help="Import private S/MIME certificate")
    group.add_option("--public", dest="public_smime", action="store_true", help="Export/Import public S/MIME certificate")
    group.add_option("--password", dest="password", action="store", help="set password")
    group.add_option("--ask-password", dest="ask_password", action="store_true", help="ask for password if needed")
    parser.add_option_group(group)

    # WebApp setting option group
    group = OptionGroup(parser, "webapp-settings", "")
    group.add_option("--language", dest="language", action="store", help="Set new language (e.g. en_GB or nl_NL)")
    group.add_option("--theme", dest="theme", action="store", help="Change theme (e.g. dark)")
    group.add_option("--free-busy", dest="freebusy", action="store", help="Change free/busy time span in months")
    group.add_option("--icons", dest="icons", action="store", help="Change icons (e.g. breeze)")
    group.add_option("--htmleditor", dest="htmleditor", action="store", help="Change the HTML editor (e.g. full_tinymce)")
    parser.add_option_group(group)

    # Advanced option group
    group = OptionGroup(parser, "Advanced", "Here be dragons")
    group.add_option("--add-option", dest="add_option", action="store", help="Add/change config option (e.g. \"settings.zarafa.v1.main.active_theme = dark\")")
    parser.add_option_group(group)

    # Show the help
    if print_help:
        parser.print_help()
        sys.exit()

    return parser.parse_args()


"""
Read user settings

:param user: The user
:return: Settings
"""
def read_settings(user):
    try:
        mapisettings = user.store.prop(PR_EC_WEBACCESS_SETTINGS_JSON).value.decode('utf-8')
        settings = json.loads(mapisettings)
    except Exception as e:
        print('{}: Has no or no valid WebApp settings creating empty config tree'.format(user.name))
        settings = json.loads('{"settings": {"zarafa": {"v1": {"contexts": {"mail": {}}}}}}')
    return settings


"""
Write WebApp setting into the user store

:param user: The user
:param setting: The setting that should be written
"""
def write_settings(user, setting):
    try:
        user.store.create_prop(PR_EC_WEBACCESS_SETTINGS_JSON, setting.encode('utf-8'))
    except Exception as e:
        print('{}: Error Writing WebApp settings for user: {}'.format(e, user.name))


"""
Reset all WebApp settings to default

:param user: The user
"""
def reset_settings(user):
    user.store.create_prop(PR_EC_WEBACCESS_SETTINGS_JSON, '{"settings": {"zarafa": {"v1": {"contexts": {"mail": {}}}}}}'.encode('utf-8'))
    print('Removed WebApp settings for user: {}'.format(user.name))


"""
Backup user setting

:param user: The user
:param location: Filename to backup to
"""
def backup(user, location=None):
    if location:
        backup_location = location
    else:
        backup_location = '.'
    webapp = read_settings(user)

    f = open('%s/%s.json' % (backup_location, user.name), 'w')
    f.write(json.dumps(webapp, sort_keys=True, indent=4, separators=(',', ': ')))
    f.close()

    print('Creating backup WebApp settings for user {}'.format(user.name))


"""
Restore user setting

:param user: The user
:param filename: Filename to restore from. If filename does not exist <user>.json is used.
"""
def restore(user, filename=None):
    if filename:
        restorename = filename
    else:
        restorename= '%s.json' % user.name
    with open(restorename) as data_file:
        data = json.load(data_file)
    print('Restoring WebApp settings for user {}'.format(user.name))
    write_settings(user, json.dumps(data))


"""
Change the language

:param user: The user
:param language: The language that should be used. Format e.g. "en_GB"
"""
def language(user, language):
    settings = read_settings(user)
    if not settings['settings']['zarafa']['v1'].get('main'):
        settings['settings']['zarafa']['v1']['main'] = {}
    settings['settings']['zarafa']['v1']['main']['language'] = locale
    print('Setting locale to: {}'.format(locale))
    write_settings(user, json.dumps(settings))


"""
Backup signature from the users store

:param user: The user
:param location: The location of the html signature
"""
def backup_signature(user, location=None):
    if location:
        backup_location = location
    else:
        backup_location = '.'
    try:
        settings = read_settings(user)
    except Exception as e:
        print('Could not load WebApp settings for user {} (Error: {})'.format(user.name, repr(e)))
        sys.exit(1)
    if settings['settings']['zarafa']['v1']['contexts']['mail'].get('signatures'):
        for item in settings['settings']['zarafa']['v1']['contexts']['mail']['signatures']['all']:
            name = settings['settings']['zarafa']['v1']['contexts']['mail']['signatures']['all'][item]['name']
            filename = '%s/%s_%s_%s.html' % (backup_location, user.name, name.replace(' ', '-'), item)
            with open(filename, 'w') as outfile:
                print('Dumping: \'{}\' to \'{}\' '.format(name, filename))
                outfile.write(settings['settings']['zarafa']['v1']['contexts']['mail']['signatures']['all'][item][
                                  'content'])
    else:
        print('user {} has no signature'.format(user.name))


"""
Restore signature into the users store

:param user: The user
:param filename: The filename of the signature 
:param replace: Remove all existing signatures for the restore signature
:param default: Set the signature as default for new mail and replies
"""
def restore_signature(user, filename, replace=None, default=None):

    restorefile = filename
    with open(restorefile, 'r') as sigfile:
        signaturehtml = sigfile.read()
    if replace:
        signatureid = filename.split('_')[2].split('.')[0]
        action = 'Replacing'
    else:
        signatureid = int(time.time())
        action = 'Adding'

    signaturename = filename.split('_')[1].replace('-',' ')
    signaturecontent = dict(
        {u'name': signaturename, u'content': signaturehtml, u'isHTML': True})
    settings = read_settings(user)

    if not settings['settings']['zarafa']['v1']['contexts'].get('mail'):
        print("{}: Adding config tree.".format(user.name))
        settings['settings']['zarafa']['v1']['contexts']['mail'] = dict({})

    if not settings['settings']['zarafa']['v1']['contexts']['mail'].get('signatures'):
        print("{}: Adding Signature settings to config tree.".format(user.name))
        settings['settings']['zarafa']['v1']['contexts']['mail']['signatures'] = dict({})

    if not settings['settings']['zarafa']['v1']['contexts']['mail']['signatures'].get('all'):
        print("{}: Empty Signature settings detected.".format(user.name))
        settings['settings']['zarafa']['v1']['contexts']['mail']['signatures'] = dict({'all': dict({})})

    print('{}: {} signature with {}' .format(user.name, action, signaturename))

    settings['settings']['zarafa']['v1']['contexts']['mail']['signatures']['all'][signatureid] = signaturecontent
    if default:
        print('Changing default signature')
        settings['settings']['zarafa']['v1']['contexts']['mail']['signatures']['new_message'] = signatureid
        settings['settings']['zarafa']['v1']['contexts']['mail']['signatures']['replyforward_message'] = signatureid

    write_settings(user, json.dumps(settings))


"""
Export S/MIME certificate from users store

:param user: The user
:param location: The location to store the certificiate. If location is empty current dir is used
:param public: Export public certificate part
"""
def export_smime(user, location=None, public=None):
    if location:
        backup_location = location
    else:
        backup_location = '.'

    certificates =list(user.store.root.associated.items())

    if len(certificates) == 0:
        print('No certificates found')
        return

    for cert in certificates:
        if public and cert.prop(PR_MESSAGE_CLASS).value == 'WebApp.Security.Public':
            extension = 'pub'
            body = cert.body.text
        else:
            extension = 'pfx'
            body = base64.b64decode(cert.body.text)

            print('found {} certificate {} (serial: {})'.format(cert.prop(PR_MESSAGE_CLASS).value, cert.subject, cert.prop(PR_SENDER_NAME).value))
            with open("%s/%s-%s.%s" % (backup_location, cert.subject, cert.prop(PR_SENDER_NAME).value, extension), "w") as text_file:
                text_file.write(body)


"""
Import S/MIME certificate into users store

:param user: The user
:param cert_file: The certificate in PKCS12 format
:param passwd: The passphrase of the certificate
:param ask_password: Ask passphrase before importing
:param public: Import public certificate part
"""
def import_smime(user, cert_file, passwd, ask_password=None, public=None):
    if ask_password:
        passwd = getpass.getpass()
    elif not passwd:
        passwd = ''

    assoc = user.store.root.associated
    with open(cert_file) as f:
        cert = f.read()
    if not public:
        messageclass = 'WebApp.Security.Private'
        try:
            p12 = OpenSSL.crypto.load_pkcs12(cert, passwd)
        except IOError as e:
            print(e)
            sys.exit(1)
        except Exception as e:
            print(e.message)
            sys.exit(1)

        certificate = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, p12.get_certificate())
        cert_data = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, certificate)
        date_before = MAPI.Time.unixtime(mktime(datetime.strptime(cert_data.get_notBefore(), "%Y%m%d%H%M%SZ" ).timetuple()))
        date_after = MAPI.Time.unixtime(mktime(datetime.strptime(cert_data.get_notAfter(), "%Y%m%d%H%M%SZ" ).timetuple()))

        issued_by = ""
        dict_issued_by = dict(cert_data.get_issuer().get_components())
        for key in dict_issued_by:
            issued_by += "%s=%s\n" % (key, dict_issued_by[key])

        issued_to = ""
        dict_issued_to = dict(cert_data.get_subject().get_components())
        for key in dict_issued_to:
            if key == 'emailAddress':
                email = dict_issued_to[key]
            else:
                issued_to += "%s=%s\n" % (key, dict_issued_to[key])

        if str(user.email) == email:
            item = assoc.mapiobj.CreateMessage(None, MAPI_ASSOCIATED)
            item.SetProps([SPropValue(PR_SUBJECT, email),
                                  SPropValue(PR_MESSAGE_CLASS, messageclass),
                                  SPropValue(PR_MESSAGE_DELIVERY_TIME, date_after),
                                  SPropValue(PR_CLIENT_SUBMIT_TIME, date_before),
                                  SPropValue(PR_SENDER_NAME, str(int(cert_data.get_serial_number()))),
                                  SPropValue(PR_SENDER_EMAIL_ADDRESS, issued_by),
                                  SPropValue(PR_SUBJECT_PREFIX, issued_to),
                                  SPropValue(PR_RECEIVED_BY_NAME,  str(cert_data.digest("sha1"))),
                                  SPropValue(PR_INTERNET_MESSAGE_ID,  str(cert_data.digest("md5"))),
                                  SPropValue(PR_BODY,  str(base64.b64encode(p12)))])
            item.SaveChanges(KEEP_OPEN_READWRITE)
            print('Imported private certificate')
        else:
            print('Email address doesn\'t match')


"""
Custom function to merge two dictionaries.
Previously we used the internal dotty function for this,
but this function caused undesired behavior

:param dict1: The first dictionary
:param dict2: The second dictionary
"""
def mergedicts(dict1, dict2):
    for k in set(dict1.keys()).union(dict2.keys()):
        if k in dict1 and k in dict2:
            if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                yield (k, dict(mergedicts(dict1[k], dict2[k])))
            else:
                yield (k, dict2[k])
        elif k in dict1:
            yield (k, dict1[k])
        else:
            yield (k, dict2[k])


"""
Inject webapp settings into the users store

:param user: The user
:param data: The webapp setting
"""
def advanced_inject(user, data):
    settings = read_settings(user)
    split_data = data.split('=')

    value = split_data[1].lstrip().rstrip()
    dot = dotty()
    dot[split_data[0].rstrip()] = value

    new_data = dot.to_dict()
    new_settings = dict(mergedicts(settings, new_data))

    write_settings(user, json.dumps(new_settings))

    
"""
Main function run with arguments
"""
def main():
    if len(sys.argv) == 1:
        opt_args(True)
    options, args = opt_args()

    # Always first!
    # If the script should execute for all users
    # The admin should pass the '--all-users' parameter
    if not options.users and not options.all_users:
        print('There are no users specified. Use "--all-users" to run for all users')
        sys.exit(1)

    for user in kopano.Server(options).users(options.users):
        # Backup and restore
        if options.backup:
            backup(user, options.location)
        if options.restore:
            restore(user, options.file)

        # Language
        if options.language:
            language(user, options.language)

        # S/MIME import/export
        if options.export_smime:
            export_smime(user, options.location, options.public_smime)
        if options.import_smime:
            import_smime(user, options.import_smime, options.password, options.ask_password, options.public_smime)

        # Signature
        if options.backup_signature:
            backup_signature(user, options.location)
        if options.restore_signature:
            restore_signature(user,  options.restore_signature, options.replace, options.default_signature)

        # Advanced injection option
        if options.add_option:
            advanced_inject(user, options.add_option)

        # Theme
        if options.theme:
            setting = 'settings.zarafa.v1.main.active_theme = {}'.format(options.theme)
            advanced_inject(user, setting)
            print('Theme changed to {}'.format(options.theme))

        # Free busy publishing
        if options.freebusy:
            if int(options.freebusy) > 36:
                options.freebusy = 36
                print('Maximum publishing months is 36. Using 36 instead.')
            setting = 'settings.zarafa.v1.contexts.calendar.free_busy_range = {}'.format(options.freebusy)
            advanced_inject(user, setting)
            if int(options.freebusy) == 0:
                print('Free/Busy publishing disabled')
            else:
                print('Free/Busy published for {} months '.format(options.freebusy))

        # Icon set
        if options.icons:
            accepted_icons = {'Breeze', 'Classic'}
            if not options.icons in accepted_icons:
                print('Valid syntax: Breeze or Classic')
                sys.exit(1)
            setting = 'settings.zarafa.v1.main.active_iconset = {}'.format(options.icons)
            advanced_inject(user, setting)
            print('icon set changed to {}'.format(options.icons))

        # Editor
        if options.htmleditor:
            accepted_editors = {'htmleditor-minimaltiny', 'full_tinymce'}
            if not options.htmleditor in accepted_editors:
                print('Valid syntax: htmleditor-minimaltiny or full_tinymce')
                sys.exit(1)
            setting = 'settings.zarafa.v1.contexts.mail.html_editor = {}'.format(options.htmleditor)
            advanced_inject(user, setting)
            print('Editor changed to {}'.format(options.htmleditor))

        # Always at last!!!
        if options.reset:
            reset_settings(user)


if __name__ == "__main__":
    main()
