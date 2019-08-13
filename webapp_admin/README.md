# WebApp Admin

>**Always make a backup of the user settings and test the new settings afterwards**

WebApp admin is a command-line interface to modify, inject and export WebApp settings.

# Example Usage

Reset WebApp settings
> python3 webapp_admin -u john --reset

Change free/busy to 36 months
> python3 webapp_admin -u john --free-busy=36

If you want to make a change for all users pass the --all-users parameter. Example:
> python3 webapp_admin --all-users --icons Breeze

# Dependencies

- python3
- python-kopano
- python-mapi
- OpenSSL
- dotty_dict

For debian 10 python3-pkg-resources is required 

# License

licensed under GNU Affero General Public License v3.
