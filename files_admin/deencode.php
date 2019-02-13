#!/usr/bin/env php
<?php
error_reporting(E_ERROR | E_WARNING | E_PARSE);

include "/etc/kopano/webapp/config-files.php";

if ( $argv[1] == 'encode' ) {
    $value = openssl_encrypt($argv[2], "des-ede3-cbc", FILES_PASSWORD_KEY, 0, FILES_PASSWORD_IV);
}
elseif  ( $argv[1] == 'decode' ) {
    $value = openssl_decrypt($argv[2], "des-ede3-cbc", FILES_PASSWORD_KEY, 0, FILES_PASSWORD_IV);
}
else {
    print "No valid options provided usage php dencode.php encode/decode string\n";
}

if ( ! empty($value) ) {
    print $value;
}
?>