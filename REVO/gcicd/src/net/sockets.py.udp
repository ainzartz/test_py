from random import randint

import socket

# network
#-------------------------------------------------------------------------------

def get_server_address():
    ''' https://stackoverflow.com/a/1267524
    '''
    try:
        return [
            (_socket.connect(('8.8.8.8', 53)),
             _socket.getsockname()[0],
             _socket.close())
            for _socket in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]
        ][0][1] or [
            address
            for address in socket.gethostbyname_ex(socket.gethostname())[2]
            if not address.startswith("127.")
        ][0]
    except IndexError:
        return '127.0.0.1'

# get random port number from unprivileged port range.
get_random_unprivileged_port = lambda: randint(1025, 65535)

# UDP sockets
#-------------------------------------------------------------------------------

def unsafe_allocate_udp_socket(host='127.0.0.1', port=None, timeout=1.0,
                               is_client=False,
                               is_reused=False):
    ''' create a UDP socket without automatic socket closure.
    '''
    # error checking for listening sockets.
    if not is_client and any([
            host not in ['127.0.0.1', 'localhost', '0.0.0.0'],
            not 1024 < port <= 65535]):
        return

    # create a UDP socket.
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp_socket.setblocking(False)
    if is_client:
        return udp_socket

    try: # bind listening sockets.
        udp_socket.settimeout(timeout)
        udp_socket.bind((host, port))
    except socket.error:
        return

    # reuse listening sockets.
    if is_reused:
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, True)
    return udp_socket

class safe_allocate_udp_server(object):
    ''' allocate exception-safe random UDP server.
    '''
    def __init__(self, port, timeout=1.0):
        self.port = port
        self.timeout = timeout
        self.__socket = None

    def __enter__(self):
        self.__socket = unsafe_allocate_udp_socket(
            host='0.0.0.0',
            port=self.port,
            is_reused=True,
            timeout=self.timeout)
        return self.__socket

    def __exit__(self, *a, **kw):
        try: self.__socket.close()
        except AttributeError:
            pass # already closed
        del self.__socket

# UDP clients
#-------------------------------------------------------------------------------

def unsafe_allocate_udp_client(timeout=1.0):
    ''' allocate a random UDP client that must be manually cleaned up.
    '''
    while not locals().get('client'):
        client = unsafe_allocate_udp_socket(is_client=True, timeout=timeout)
    return client

class safe_allocate_udp_client(object):
    ''' allocate exception-safe random UDP client.
    '''
    def __init__(self, timeout=1.0):
        self.timeout = timeout
        self.__socket = None

    def __enter__(self):
        self.__socket = unsafe_allocate_udp_client(self.timeout)
        return self.__socket

    def __exit__(self, *a, **kw):
        try: self.__socket.close()
        except AttributeError:
            pass # already closed
        del self.__socket

# UDP server
#-------------------------------------------------------------------------------

def unsafe_allocate_random_udp_socket(is_reused=False):
    ''' allocate a random listening UDP socket that must be manually cleaned up.
    '''
    _socket = None
    host = '0.0.0.0'
    while not _socket:
        port = get_random_unprivileged_port()
        _socket = unsafe_allocate_udp_socket(host=host, port=port, is_reused=is_reused)
    return _socket

class safe_allocate_random_udp_socket(object):
    ''' allocate exception-safe random listening UDP socket.
    '''
    def __init__(self, is_reused=False):
        self.is_reused = is_reused
        self.__socket = None

    def __enter__(self):
        self.__socket = unsafe_allocate_random_udp_socket(self.is_reused)
        return self.__socket

    def __exit__(self, *a, **kw):
        try: self.__socket.close()
        except AttributeError:
            pass # already closed
        del self.__socket

"""
"""
if __name__ == '__main__':
	import sys
	call_id = sys.argv[1]
	with safe_allocate_udp_client() as client:
        	    client.sendto('C310|'+ call_id, ('105.20.2.36', 5810))
