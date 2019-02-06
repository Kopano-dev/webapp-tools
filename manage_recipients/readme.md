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


