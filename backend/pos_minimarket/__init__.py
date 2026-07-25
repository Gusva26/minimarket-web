import socket

# Force IPv4 socket resolution for SMTP and DB connections on cloud platforms without IPv6 (e.g. Render)
_orig_getaddrinfo = socket.getaddrinfo

def _ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    if host and ('smtp' in str(host) or host == 'smtp.gmail.com') or family == 0:
        family = socket.AF_INET
    return _orig_getaddrinfo(host, port, family, type, proto, flags)

socket.getaddrinfo = _ipv4_getaddrinfo

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass