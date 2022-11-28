#!/bin/sh

## 
# Change the name of the cert/key file if needed
##
CERT='certfile.cert'
KEY='keyfile.key'

openssl req -x509 \
            -nodes \
            -newkey rsa:4096 \
            -keyout $KEY \
            -out $CERT \
            -days 3650