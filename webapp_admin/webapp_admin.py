#!/usr/bin/env python3
# encoding: utf-8
from pkg_resources import parse_version
import sys
try:
    import kopano
except ImportError:
    print('python-kopano should be installed on your system')
    sys.exit(1)
try:
    from MAPI.Tags import (
        PR_EC_WEBACCESS_SETTINGS_JSON, PR_LANGUAGE, PR_EC_WEBAPP_PERSISTENT_SETTINGS_JSON_W, 
        PR_MESSAGE_CLASS_W, PR_SENDER_NAME_W, PR_SUBJECT, PR_MESSAGE_CLASS, 
        PR_MESSAGE_DELIVERY_TIME,PR_CLIENT_SUBMIT_TIME, PR_SENDER_NAME, 
        PR_SENDER_EMAIL_ADDRESS, PR_SUBJECT_PREFIX, PR_RECEIVED_BY_NAME, PR_INTERNET_MESSAGE_ID, 
        PR_BODY, PR_MESSAGE_DELIVERY_TIME
        )
except ImportError:
    print('python-mapi should be installed on your system')
    sys.exit(1)
import json
import base64
try:
    import OpenSSL.crypto
except ImportError:
    pass
import binascii
from datetime import datetime, timedelta
from time import mktime
import getpass
import time
from functools import reduce
from operator import getitem
from optparse import OptionGroup

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

    # Addionals stores group
    group = OptionGroup(parser, "Store", "")
    group.add_option("--add-store",   dest="add_store", action="store", help="Add shared store")
    group.add_option("--del-store",   dest="del_store", action="store", help="Delete shared store")
    group.add_option("--folder-type", dest="folder_type", action="store", help="Folder to add")
    group.add_option("--subfolder",  dest="sub_folder", action="store_true", help="Add subfolders")
    group.add_option("--list-stores", dest="list_stores", action="store_true", help="List shared stores")
    parser.add_option_group(group)

    # Signature option group
    group = OptionGroup(parser, "Signature", "")
    group.add_option("--backup-signature", dest="backup_signature", action="store_true", help="Backup signature")
    group.add_option("--restore-signature", dest="restore_signature", action="store", help="Restore signature (need file name)")
    group.add_option("--replace-signature", dest="replace_signature", action="store", help="Replace existing signature, file layout must be: username_signature-name_signatureid.html or signature-name_signatureid.html ")
    group.add_option("--default-signature", dest="default_signature", action="store_true", help="Set signature as default one")
    parser.add_option_group(group)

    # Categories setting option group
    group = OptionGroup(parser, "Categories", "")
    group.add_option("--export-categories", dest="export_categories", action="store_true", help="Export Categories (name and color)")
    group.add_option("--import-categories", dest="import_categories", action="store_true", help="Import Categories (name and color)")
    parser.add_option_group(group)

    # S/MIME option group
    group = OptionGroup(parser, "S/MIME", "")
    group.add_option("--export-smime", dest="export_smime", action="store_true", help="Export private S/MIME certificate")
    group.add_option("--import-smime", dest="import_smime", action="store", help="Import private S/MIME certificate")
    group.add_option("--remove-expired", dest="remove_expired", action="store_true", help="Remove expired public S/MIME certificates")
    group.add_option("--public", dest="public_smime", action="store_true", help="Export/Import public S/MIME certificate")
    group.add_option("--password", dest="password", action="store", help="set password")
    group.add_option("--ask-password", dest="ask_password", action="store_true", help="ask for password if needed")
    parser.add_option_group(group)
    
    # Sendas option group
    # Note: code wise we use 'sendas' similar to WebApp.
    # The feature is called 'from addresses' and this is also what the user sees in WebApp settings.
    group = OptionGroup(parser, "Sendas", "")
    group.add_option("--list-from-address", dest="list_sendas", action="store_true", help="List sent from addresses")
    group.add_option("--add-sent-from", dest="add_sendas", action="store_true", help="Create new sent from address")
    group.add_option("--del-sent-from", dest="del_sendas", action="store", metavar="NUMBER", type="int", help="Delete sent from address")
    group.add_option("--change-sent-from", dest="change_sendas", action="store", metavar="NUMBER", type="int", help="Change sent from address")
    group.add_option("--sent-from-name", dest="sendas_name", action="store", help="Display name")
    group.add_option("--sent-from-email,", dest="sendas_email", action="store", help="Email address")
    group.add_option("--sent-from-alias", dest="sendas_alias", action="store_true", help="add all alias addresses of user to sent from list")
    group.add_option("--sent-from-forward", dest="sendas_forward", action="store_true", help="Set as default forward address")
    group.add_option("--sent-from-new", dest="sendas_new", action="store_true", help="Set as default new email address")
    group.add_option("--sent-from-reply", dest="sendas_reply", action="store_true", help="Set as default reply address")
    parser.add_option_group(group)
    
    # WebApp setting option group
    group = OptionGroup(parser, "webapp-settings", "")
    group.add_option("--language", dest="language", action="store", type="string", help="Set new language (e.g. en_GB or nl_NL)")
    group.add_option("--theme", dest="theme", action="store", help="Change theme (e.g. dark)")
    group.add_option("--free-busy", dest="freebusy", action="store", help="Change free/busy time span in months")
    group.add_option("--icons", dest="icons", action="store", help="Change icons (e.g. breeze)")
    group.add_option("--htmleditor", dest="htmleditor", action="store", help="Change the HTML editor (e.g. full_tinymce)")
    group.add_option("--remove-state", dest="remove_state", action="store_true", help="Remove all the state settings")
    group.add_option("--add-safesender", dest="add_sender", action="store", help="Add domain to safe sender list")
    group.add_option("--polling-interval", dest="polling_interval", action="store", help="Change the polling interval (seconds)")
    group.add_option("--calendar-resolution", dest="calendar_resolution", action="store", help="Change the calendar resolution (minutes)")
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
    # Get language from PR_LANGUAGE
    if language == 'userdefined':
        try:
            language = user.prop(PR_LANGUAGE).value
        except:
            print('User language is not defined using en_GB as fallback')
            language = 'en_GB'

    if not settings['settings']['zarafa']['v1'].get('main'):
        settings['settings']['zarafa']['v1']['main'] = {}
    settings['settings']['zarafa']['v1']['main']['language'] = language
    print('Setting locale to: {}'.format(language))
    write_settings(user, json.dumps(settings))


"""
Add shared store
"""
def add_store(user, user_to_add, folder_type, subfolder=False):
    allowed_folder_types = ["all", "inbox", "calendar", "contact", "note", "task"]
    if folder_type not in allowed_folder_types:
        print("Unknown folder type allowed: {}".format(','.join(allowed_folder_types)))
        sys.exit(1)

    settings = read_settings(user)
    if not settings['settings']['zarafa']['v1']['contexts'].get('hierarchy') or not settings['settings']['zarafa']['v1']['contexts']['hierarchy'].get('shared_stores'):
        settings['settings']['zarafa']['v1']['contexts']['hierarchy']['shared_stores'] = {}

    settings['settings']['zarafa']['v1']['contexts']['hierarchy']['shared_stores'][user_to_add]= {folder_type : {'folder_type': folder_type, 'show_subfolders': subfolder}}
    print("Saving settings")
    write_settings(user, json.dumps(settings))


"""
Delete shared store 
"""
def del_store(user, user_to_del, folder_type=None):
    if folder_type:
        allowed_folder_types = ["all", "inbox", "calendar", "contact", "note", "task"]
        if folder_type not in allowed_folder_types:
            print("Unknown folder type allowed: {}".format(','.join(allowed_folder_types)))
            sys.exit(1)
    

    settings = read_settings(user)
    if not settings['settings']['zarafa']['v1']['contexts'].get('hierarchy') or not settings['settings']['zarafa']['v1']['contexts']['hierarchy'].get('shared_stores'):
        print("No additional stores found")
        return

    shared_store = settings['settings']['zarafa']['v1']['contexts']['hierarchy']['shared_stores'].get(user_to_del)
    if not shared_store:
        print("No additional stores found")
        return
    try:
        if not folder_type:
            settings['settings']['zarafa']['v1']['contexts']['hierarchy']['shared_stores'].pop(user_to_del)
        else:
            settings['settings']['zarafa']['v1']['contexts']['hierarchy']['shared_stores'][user_to_del].pop(folder_type)
    except KeyError:
        pass
    print("Saving settings")
    write_settings(user, json.dumps(settings))

"""
List all added stores
"""
def list_stores(user):
    settings = read_settings(user) 

    try:
        stores =  settings['settings']['zarafa']['v1']['contexts']['hierarchy']['shared_stores']
    except KeyError:
        print("No additional stores found")
        return
    table_header = ["User", 'Folder type', 'Show subfolders']
    table_data =[]
    for user in stores:
        for folder in stores[user]:
            table_data.append([user, folder, stores[user][folder]['show_subfolders']])

    print(get_pretty_table(table_data, table_header))
    
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
    if not settings['settings']['zarafa']['v1']['contexts'].get("mail"):
        settings['settings']['zarafa']['v1']['contexts']['mail'] = {}
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
    filename_split = filename.split('_')
    
    if len(filename_split) == 2:
        signaturename = filename_split[0].replace('-',' ')
        if replace:
            signatureid  = filename_split[1].split('.')[0]
    elif len(filename_split) == 3:
        signaturename = filename_split[1].replace('-',' ')
        if replace:
            signatureid = filename_split[2].split('.')[0]
    else:
        if replace:
            print('File format is not supported')
            sys.exit(1)

    with open(restorefile, 'r') as sigfile:
        signaturehtml = sigfile.read()

    if replace:
        action = 'Replacing'
    else:
        signaturename = filename.split('.')[0]
        signatureid = int(time.time())
        action = 'Adding'

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
Export categories from users store

:param user: The user
:param location: The location to store the certificiate. If location is empty current dir is used
"""
def export_categories(user, location=None):
    if location:
        backup_location = location
    else:
        backup_location = '.'
    # first check if persistent settings exist
    if not user.store.get_prop(PR_EC_WEBAPP_PERSISTENT_SETTINGS_JSON_W):
        print('Categories are not customized yet, so nothing to export')

    persistent_settings =  json.loads(user.store.prop(PR_EC_WEBAPP_PERSISTENT_SETTINGS_JSON_W).value)

    # Get categories
    if not persistent_settings['settings']['kopano']['main'].get('categories'):
        print('Categories are not customized yet, so nothing to export')

    categories = persistent_settings['settings']['kopano']['main']['categories']
    f = open('%s/%s-categories.json' % (backup_location, user.name), 'w')
    f.write(json.dumps(categories, sort_keys=True, indent=4, separators=(',', ': ')))
    f.close()

    print('Creating categories backup for user {}'.format(user.name))


"""
Import categories from users store

:param user: The user
:param filename: The filename of the signature
"""
def import_categories(user, filename=None):
    if filename:
        restorename = filename
    else:
        restorename= '%s-categories.json' % user.name
    with open(restorename) as data_file:
        data = json.load(data_file)

    if not user.store.get_prop(PR_EC_WEBAPP_PERSISTENT_SETTINGS_JSON_W):
        persistent_settings ={'settings': {'kopano': {'main': {'categories':data}}}}
    else:
        persistent_settings = json.loads(user.store.get_prop(PR_EC_WEBAPP_PERSISTENT_SETTINGS_JSON_W).value)
        persistent_settings['settings']['kopano']['main']['categories'] = data

    print('Restoring categories for user {}'.format(user.name))
    user.store.create_prop(PR_EC_WEBAPP_PERSISTENT_SETTINGS_JSON_W, json.dumps(persistent_settings))


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
        if public and cert.prop(PR_MESSAGE_CLASS_W).value == 'WebApp.Security.Public':
            extension = 'pub'
            body = cert.text
        else:
            extension = 'pfx'
            body = base64.b64decode(cert.text)

            print('found {} certificate {} (serial: {})'.format(cert.prop(PR_MESSAGE_CLASS_W).value, cert.subject, cert.prop(PR_SENDER_NAME_W).value))
            with open("%s/%s-%s.%s" % (backup_location, cert.subject, cert.prop(PR_SENDER_NAME_W).value, extension), "wb") as text_file:
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
    if not sys.modules.get('OpenSSL'):
        print('PyOpenSSl not installed \npip3 install pyOpenSSL')
        sys.exit(1)
    if ask_password:
        passwd = getpass.getpass()
    elif not passwd:
        passwd = ''

    assoc = user.store.root.associated
    with open(cert_file, 'rb') as f:
        cert = f.read()
    if not public:
        messageclass = 'WebApp.Security.Private'
        try:
            p12 = OpenSSL.crypto.load_pkcs12(cert, passwd)
        except IOError as e:
            print(e)
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)

        certificate = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, p12.get_certificate())
        cert_data = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, certificate)
        date_before = MAPI.Time.unixtime(mktime(datetime.strptime(cert_data.get_notBefore().decode('utf-8'), "%Y%m%d%H%M%SZ" ).timetuple()))
        date_after = MAPI.Time.unixtime(mktime(datetime.strptime(cert_data.get_notAfter().decode('utf-8'), "%Y%m%d%H%M%SZ" ).timetuple()))

        issued_by = ""
        dict_issued_by = dict(cert_data.get_issuer().get_components())
        for key in dict_issued_by:
            issued_by += "%s=%s\n" % (key, dict_issued_by[key])

        issued_to = ""
        dict_issued_to = dict(cert_data.get_subject().get_components())
        for key in dict_issued_to:
            if key == b'emailAddress':
                email = dict_issued_to[key].decode('utf-8')
            else:
                issued_to += "%s=%s\n" % (key, dict_issued_to[key])

        if user.email == email:
            item = assoc.mapiobj.CreateMessage(None, MAPI_ASSOCIATED)

            item.SetProps([SPropValue(PR_SUBJECT, email.encode('utf-8')),
                           SPropValue(PR_MESSAGE_CLASS, messageclass.encode('utf-8')),
                           SPropValue(PR_MESSAGE_DELIVERY_TIME, date_after),
                           SPropValue(PR_CLIENT_SUBMIT_TIME, date_before),
                           SPropValue(PR_SENDER_NAME, str(cert_data.get_serial_number()).encode('utf-8')),
                           SPropValue(PR_SENDER_EMAIL_ADDRESS, issued_by.encode('utf-8')),
                           SPropValue(PR_SUBJECT_PREFIX, issued_to.encode('utf-8')),
                           SPropValue(PR_RECEIVED_BY_NAME,  cert_data.digest("sha1")),
                           SPropValue(PR_INTERNET_MESSAGE_ID,  cert_data.digest("md5")),
                           SPropValue(PR_BODY,  base64.b64encode(p12.export()))])
            item.SaveChanges(KEEP_OPEN_READWRITE)
            print('Imported private certificate')
        else:
            print('Email address doesn\'t match')

"""
Remove expired S/MIME Public certificates

:param user: The user
"""
def remove_expired_smime(user):
    # unable to loop over the associated items so getting the items in a list instead
    certificates =list(user.store.root.associated.items())

    if len(certificates) == 0:
        print('No certificates found')
        return

    now = datetime.now()
    for cert in certificates:
        # We only want to remove the public certificate
        if cert.prop(PR_MESSAGE_CLASS_W).value == 'WebApp.Security.Public':
            if cert.prop(PR_MESSAGE_DELIVERY_TIME).value < now:
                print('deleting public certificate {} ({})'.format(cert.subject, cert.prop(PR_MESSAGE_DELIVERY_TIME).value))
                user.store.root.associated.delete(cert)
    
"""
List sendas addresses

:param user: The user
"""
def list_sendas(user):
    setting = read_settings(user)
    sendas = (setting['settings']['zarafa']['v1']['contexts']['mail'].get('sendas', []))
    table_header = ["ID", "Name", 'Email', 'Reply mail', 'New mail', 'Forward mail']
    table_data =[]
    check = u"\u2714"
    uncheck = u"\u2716"
    for l in sendas:
        forward = uncheck
        reply = uncheck
        new = uncheck
        if l['forward_mail']:
            forward = check
        if l['reply_mail']:
            reply = check
        if l['new_mail']:
            new  = check    
        table_data.append([l['rowid'], l['display_name'], l['smtp_address'],reply, new, forward])

    print(get_pretty_table(table_data, table_header))
    
"""
Add sendas address

:param user: The user
:param sendas_name: The name of the sendas address
:param sendas_email: The email address of the sendas address
:param sendas_forward: Set as default forward address 
:param sendas_new: Set as default address for new email
:param sendas_reply: Set as default reply address
:param alias: Set all aliasses of user as sendas address

"""
def add_sendas(user, sendas_name, sendas_email, alias, sendas_forward=False, sendas_new=False, sendas_reply=False):
    settings = read_settings(user)
    sendas = settings['settings']['zarafa']['v1']['contexts']['mail'].get('sendas', [])
    rowid = 0
    if len(sendas) > 0:
        rowid = sendas[-1].get('rowid', 0) + 1
    if not alias:
        if not sendas_name or not sendas_email:
            print('--sendas-name and --sendas-email are mandatory')
            sys.exit(1)
        print('Creating sendas line for {}'.format(sendas_email) )
        entryid =  binascii.hexlify(user.server.ab.CreateOneOff(sendas_name, "SMTP", sendas_email, MAPI_SEND_NO_RICH_INFO| MAPI_UNICODE)).decode()
        sendas.append({
            "address_type": "SMTP",
            "display_name": sendas_name,
            "display_type": 6, 
            "display_type_ex": 0,
            "email_address": "",
            "entryid": entryid,
            "forward_mail": sendas_forward,
            "new_mail": sendas_new,
            "object_type": 6,
            "recipient_type": 0,
            "reply_mail": sendas_reply,
            "rowid": rowid,
            "search_key": "",
            "smtp_address": sendas_email
        })
    else:
        print('Writing alias addresses to sendas list')
        for address in user.prop(0x800f101f).value:
            ## ignore the address that starts with SMTP as this is the main email address
            if address.startswith("SMTP"):
               continue
            email = address.replace("smtp:","")
            entryid =  binascii.hexlify(user.server.ab.CreateOneOff(email, "SMTP", email, MAPI_SEND_NO_RICH_INFO| MAPI_UNICODE)).decode()
            sendas.append({
                "address_type": "SMTP",
                "display_name": email,
                "display_type": 6, 
                "display_type_ex": 0,
                "email_address": "",
                "entryid": entryid,
                "forward_mail": False,
                "new_mail": False,
                "object_type": 6,
                "recipient_type": 0,
                "reply_mail": False,
                "rowid": rowid,
                "search_key": "",
                "smtp_address": email
            })
            rowid += 1
    
    settings['settings']['zarafa']['v1']['contexts']['mail']['sendas'] = sendas
    write_settings(user, json.dumps(settings))

    list_sendas(user)
"""
Delete sendas address

:param user: The user
:param del_sendas: Number of row that needs to be deleted 

"""
def del_sendas(user, del_sendas):
    settings = read_settings(user)
    sendas = settings['settings']['zarafa']['v1']['contexts']['mail'].get('sendas', [])
    delete = None
    num  = 0
    
    for l in sendas:
        if l['rowid'] == del_sendas:
            delete = num
            break
        num += 1

    if delete is not None:
        sendas.pop(delete)
        print('removing row {}'.format(del_sendas))

    settings['settings']['zarafa']['v1']['contexts']['mail']['sendas'] = sendas
    write_settings(user, json.dumps(settings))

    list_sendas(user)

"""
Change sendas address

:param user: The user
:param change_sendas: Number of row that needs to be changed
:param sendas_name: The name of the sendas address
:param sendas_email: The email address of the sendas address
:param sendas_forward: Set as default forward address 
:param sendas_new: Set as default address for new email
:param sendas_reply: Set as default reply address
"""
def change_sendas(user, change_sendas, sendas_name, sendas_email, sendas_forward, sendas_new, sendas_reply):
    settings = read_settings(user)
    sendas = settings['settings']['zarafa']['v1']['contexts']['mail'].get('sendas', [])
    changed = None
    for l in sendas:
        if l['rowid'] == change_sendas:
            if sendas_name:
                changed = True
                l['display_name'] = sendas_name
            if sendas_email:
                changed = True
                l['smtp_address'] = sendas_email
            if sendas_forward != l['forward_mail']:
                changed = True
                l['forward_mail'] = sendas_forward
            if sendas_new != l['new_mail']:
                changed = True
                l['new_mail'] = sendas_new
            if sendas_reply != l['reply_mail']:
                changed = True
                l['reply_mail'] = sendas_reply

    if changed:
        print('Writing new sendas settings')
        settings['settings']['zarafa']['v1']['contexts']['mail']['sendas'] = sendas
        write_settings(user, json.dumps(settings))

    list_sendas(user)        

"""
Inject webapp settings into the users store

:param user: The user
:param data: The webapp setting
"""
def advanced_inject(user, data, value_type='string'):
    settings = read_settings(user)
    split_data = data.split('=')

    value = split_data[1].lstrip().rstrip()
    if value.lower() == 'true':
        value = True
    elif value.lower() == 'false':
        value = False
    if value_type == 'list':
        value = value.split(',')
    
    # Create new nested json if needed
    keys =  split_data[0].strip().split('.')
    reduce(getitem, keys[:-1], settings)[keys[-1]] = value

    write_settings(user, json.dumps(settings))

def get_pretty_table(iterable, header):
    max_len = [len(x) for x in header]
    for row in iterable:
        row = [row] if type(row) not in (list, tuple) else row
        for index, col in enumerate(row):
            if max_len[index] < len(str(col)):
                max_len[index] = len(str(col))
    output = '-' * (sum(max_len) + 1) + '\n'
    output += '|' + ''.join([h + ' ' * (l - len(h)) + '|' for h, l in zip(header, max_len)]) + '\n'
    output += '-' * (sum(max_len) + 1) + '\n'
    for row in iterable:
        row = [row] if type(row) not in (list, tuple) else row
        output += '|' + ''.join([str(c) + ' ' * (l - len(str(c))) + '|' for c, l in zip(row, max_len)]) + '\n'
    output += '-' * (sum(max_len) + 1) + '\n'
    return output


"""
Main function run with arguments
"""
def main():
    if len(sys.argv) == 1:
        opt_args(True)
    options, args = opt_args()

    # If the script should execute for all users
    # The admin should pass the '--all-users' parameter
    if not options.users and not options.all_users:
        print('There are no users specified. Use "--all-users" to run for all users')
        sys.exit(1)

    server = kopano.Server(options)

    for user in server.users(options.users):
        # Backup and restore
        if options.backup:
            backup(user, options.location)
        if options.restore:
            restore(user, options.file)

        # Language
        if options.language:
            language(user, options.language)

        if options.add_store:
            add_store(user, options.add_store, options.folder_type, options.sub_folder)

        if options.del_store:
            del_store(user, options.del_store, options.folder_type)

        if options.list_stores:
            list_stores(user)

        #Categories
        if options.export_categories:
            export_categories(user, options.file)
        if options.import_categories:
            import_categories(user, options.file)

        # S/MIME import/export
        if options.export_smime:
            export_smime(user, options.location, options.public_smime)
        if options.import_smime:
            import_smime(user, options.import_smime, options.password, options.ask_password, options.public_smime)
        if options.remove_expired:
            remove_expired_smime(user)

        # Signature
        if options.backup_signature:
            backup_signature(user, options.location)
        if options.restore_signature:
            restore_signature(user,  options.restore_signature, False, options.default_signature)
        if options.replace_signature:
            restore_signature(user,  options.replace_signature, True, options.default_signature)

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
            print('Icon set changed to {}'.format(options.icons))

        # Editor
        if options.htmleditor:
            accepted_editors = {'htmleditor-minimaltiny', 'full_tinymce'}
            if not options.htmleditor in accepted_editors:
                print('Valid syntax: htmleditor-minimaltiny or full_tinymce')
                sys.exit(1)
            setting = 'settings.zarafa.v1.contexts.mail.html_editor = {}'.format(options.htmleditor)
            advanced_inject(user, setting)
            print('Editor changed to {}'.format(options.htmleditor))

        # State settings
        if options.remove_state:
            settings = read_settings(user)
            settings['settings']['zarafa']['v1']['state'] = {}
            write_settings(user, json.dumps(settings))
            print('Removed state settings for {}'.format(user.name))

        # Add sender to safe sender list
        if options.add_sender:
            settings = read_settings(user)
            setting = 'settings.zarafa.v1.contexts.mail.safe_senders_list = {}'.format(options.add_sender)
            advanced_inject(user, setting, 'list')
            print('{}'.format(options.add_sender), 'Added to safe sender list for {}'.format(user.name))

        # Polling interval
        if options.polling_interval:
            try:
                value = int(options.polling_interval)
            except ValueError:
                print('Invalid number used. Please specify the value in seconds')
                sys.exit(1)
            settings = read_settings(user)
            setting = 'settings.zarafa.v1.main.reminder.polling_interval = {}'.format(options.polling_interval)
            advanced_inject(user, setting)
            print('Polling interval changed to', '{}'.format(options.polling_interval), 'for {}'.format(user.name))

        # Calendar resolution (zoom level)
        if options.calendar_resolution:
            try:
                value = int(options.calendar_resolution)
            except ValueError:
                print('Invalid number used. Please specify the value in minutes')
                sys.exit(1)
            if value < 5 or value > 60:
                print('Unsupported value used. Use a number between 5 and 60')
                sys.exit(1)
            settings = read_settings(user)
            setting = 'settings.zarafa.v1.contexts.calendar.default_zoom_level = {}'.format(options.calendar_resolution)
            advanced_inject(user, setting)
            print('Calendar resolution changed to', '{}'.format(options.calendar_resolution), 'for {}'.format(user.name))

        # Sendas
        if options.list_sendas:
            list_sendas(user)

        if options.add_sendas:
            add_sendas(user, options.sendas_name, options.sendas_email, options.sendas_alias,
            options.sendas_forward, options.sendas_new, options.sendas_reply)

        if options.del_sendas:
            del_sendas(user, options.del_sendas)
        
        if options.change_sendas:
            change_sendas(user, options.change_sendas,options.sendas_name, options.sendas_email, 
            options.sendas_forward, options.sendas_new, options.sendas_reply)

        # Always at last!!!
        if options.reset:
            reset_settings(user)


if __name__ == "__main__":
    main()
