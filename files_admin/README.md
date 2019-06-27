# Files Admin

Files admin is a command-line interface to modify, inject and export kopano-files settings.

# Files backend supported

* SMB
* Owncloud
* Webddav

# Example Usage

Inject settings from owncloud and smb config file
> python files_admin -user John --file owncloud.cfg,smb.cfg

Use the username and password provided in the config file
> python files_admin -user John --file owncloud.cfg,smb.cfg --default

# Dependencies

- python-kopano
- python-mapi

# License

licensed under GNU Affero General Public License v3.