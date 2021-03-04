# WebApp Admin

>**Always make a backup of the user settings and test the new settings afterwards**

WebApp admin is a command-line interface to modify, inject and export WebApp settings.

# Example Usage

Overview of all options:
> python3 webapp_admin -h

Reset WebApp settings
> python3 webapp_admin -u john --reset

Change free/busy to 36 months
> python3 webapp_admin -u john --free-busy=36

If you want to make a change for all users pass the --all-users parameter. Example:
> python3 webapp_admin --all-users --icons Breeze

## Signatures

To restore, replace and backup signatures we need a two part, underscore separated filename consisting of a `name` and `id`.\

Example single user: `this-is-my-signature_1234.html`\

---
**Note**\
The hypens in the filename will be displayed as spaces in WebApp\
The username can also be part of the .html file, but is then ignored by the script.
In WebApp the ID is created based on the unix time, so the ID can be anything

---

Examples

Backup signature for user `henk`
> python3 webapp_admin -u henk --backup-signature

Restore signature for user `henk`
> python3 webapp_admin -u henk --restore-signature my-cool-signature_1615141312112.html

Replace signature for user `henk`
> python3 webapp_admin -u henk --replace-signature my-cool-signature_1615141312112.html

Restore signatures for all users
> python3 webapp_admin --all-users --restore-signature mycompany-signature_1412130992124.html


# Dependencies

- python3
- python-kopano
- python-mapi
- OpenSSL
- dotty_dict
- tabulate

For debian 10 python3-pkg-resources is required

# License

licensed under GNU Affero General Public License v3.
