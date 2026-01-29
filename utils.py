import socket

def resolve_host(hostname):
    try:
        return socket.gethostbyname(hostname)
    except Exception:
        return None



