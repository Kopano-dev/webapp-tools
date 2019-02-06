# WebApp Admin

>**This tool is under contruction. Use caution on a live server. Always make a backup of the user settings and test first before modifing**

WebApp admin is a command-line interface to modify, inject and export WebApp settings.

# Example Usage

Reset WebApp settings
> python3 webapp_admin -u john --reset

Change free/busy to 36 months
> python3 webapp_admin -u john --free-busy=36

# Dependencies

- python3
- python-kopano
- python-mapi
- OpenSSL
- dotty_dict