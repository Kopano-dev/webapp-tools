Inject-files.py
===============

Script to inject the files setting into the users profile.


Files backend supported
=======================

* SMB
* Owncloud
* Webddav


Examples
========

    python inject-files -user test --file owncloud.cfg,smb.cfg

Use the username and password provided in the configfile

    python inject-files -user test --file owncloud.cfg,smb.cfg  --default




