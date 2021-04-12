## WebApp Admin

>**Always make a backup of the user settings and test the new settings afterwards**

WebApp admin is a command-line interface to modify, inject and 
export WebApp settings.

- [Dependencies](#dependencies)
- [Examples](#examples)
  - [Stores](#stores)
  - [Signatures](#signatures)
  - [Categories](#categories)
  - [From addresses (sendas)](#from-addresses-sendas)
  - [Settings](#settings)
  - [Advanced](#advanced)
- [License](#license)

# Dependencies

- python3
- python-kopano
- python-mapi
- OpenSSL
- binascii

For debian 10 python3-pkg-resources is required


# Examples   

Reset WebApp settings
```python
kopano-webapp-admin -u john --reset
```

Backup settings
```python
kopano-webapp-admin -u john --backup
```

Restore settings
```python
kopano-webapp-admin -u john --restore
```

Restore from different user
```python
kopano-webapp-admin -u john --restore --file marty.json
```

## Stores

**Please note that adding a shared store will not update the permissions, you need to use `kopano-mailbox-permissions` for this**

List stores

```python
kopano-webapp-admin -u john --list-stores
```

Add complete store
```python
kopano-webapp-admin -u john --add-store marty --folder-type all
```

Add folder with subfolders

**available folder types are `all, inbox calendar contact note or task`**

```python 
kopano-webapp-admin -u john --add-store marty --folder-type inbox --subfolder
```

Delete shared store
```python
kopano-webapp-admin -u john --del-store marty
```

## Signatures

To restore, replace and backup signatures we need a two part, underscore separated filename consisting of a `name` and `id`.

Example single user: `this-is-my-signature_1234.html` 


**The hypens in the filename will be displayed as spaces in WebApp The username can also be part of the .html file, but is then ignored by the script. In WebApp the ID is created based on the unix time, so the ID can be anything**


Backup signature
```python
kopano-webapp-admin -u john --backup-signature
```
Restore signature
```python
kopano-webapp-admin -u john --restore-signature my-cool-signature_1615141312112.html
```
Replace signature 
```python
kopano-webapp-admin -u john --replace-signature my-cool-signature_1615141312112.html
```
Restore signatures for all users
```python
kopano-webapp-admin --all-users --restore-signature mycompany-signature_1412130992124.html
```

## Categories
Export categories 
```python
kopano-webapp-admin -u john --export-categories
```
import categories from different user
```python
kopano-webapp-admin -u john --import-categories --file marty-categories.json
```

## From addresses (sendas)

List from addresses:
```python
kopano-webapp-admin -u john --list-from-address 
```
Add from address
```python
kopano-webapp-admin -u john --add-sent-from --sent-from-name Marty --sent-from-email marty@example.com
```
Add all alias addresses 

**Script will not check for duplicates**
```python
kopano-webapp-admin -u john --add-sent-from --sent-from-alias
```

**For change and delete the number can be found when listing the from addresses**

Change address 
```python
kopano-webapp-admin -u john --change-sent 1 --sent-from-name Jonas
```
Delete address 
```python
kopano-webapp-admin -u john --del-sent-from 1
```

## Settings

Change free/busy to 36 months
```python
kopano-webapp-admin -u john --free-busy=36
```


## Advanced

**Be carefull with this option as you will corrupt your settings if you have no idea what you are doing**

With the add-option parameter you are able to change any setting for webapp. You always need to supply the fully nested directory. 

Change default reminder time
```python
kopano-webapp-admin -u john --add-option "settings.zarafa.v1.contexts.calendar.default_reminder_time=20"
```

# License

licensed under GNU Affero General Public License v3.
