manage_recipients.py
====================
Manage recipients in webapp


#### Usage:

###### List recipients

```python
python remove_recipients.py --user <user>  --list
```
###### Remove recipient
Remove options is searching in display_name, smtp_address or email_address. 

```python
python remove_recipients.py --user <user>  --remove <recipient name>
```
    
###### Clear history 

```python
python remove_recipients.py --user <user>  --remove-all
```
    
#### Example

Remove all recipients that have example.com in there display_name, smtp_address or email_address

```python
python remove_recipients.py --user user  --remove example.com
```  


webapp_settings.py
==================

#### Usage:


###### Backup 

```python
python webapp_settings.py --user user  --backup
```  


###### Restore 

```python
python webapp_settings.py --user user  --restore
```  

dump_webapp_signatures.py
=========================
Dumps all the signatures in a users Webapp to seperate files, meant as companion to the script setdefaultsignature.py as delivered with Webapp (see /usr/share/doc/kopano-webapp/scripts/signatures/ on your Webapp server.)
The files will be written in the current directory.

#### Usage:
```
python dump_webapp_signatures.py --user user
```  

webapp_switch_locale.py
=========================
List or change the locale currently set in the user's WebApp settings.

#### Usage:
###### List locale
```
python switchlocale.py --user user1 
Original locale: nl_NL.UTF-8
```
###### Change locale
```
python switchlocale.py --user user1 --locale de_DE.UTF-8
Original locale: nl_NL.UTF-8
Setting locale to: de_DE.UTF-8
```


