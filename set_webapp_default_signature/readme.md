

# set_webapp_default_signature.py

Add and set a Default signature in Webapp for user(s), will overwrite any other default.
Please use a signature as dumped with dump_webapp_signatures.py

## Examples

### Set signature of a local user on the local server
```
./set_webapp_default_signature.py -u user1 -f user2-signature.sig
```  

### Set signature multiple local users on the local server
```
./set_webapp_default_signature.py -u user1 -u user3 -f user2-signature.sig
```

### Set signature for all local users on the local server
```
./set_webapp_default_signature.py -a -f user2-signature.sig
```


