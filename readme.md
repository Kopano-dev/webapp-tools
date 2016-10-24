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
```python
python dump_webapp_signatures.py --user user
```  
