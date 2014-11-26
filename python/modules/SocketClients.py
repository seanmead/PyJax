"""
Created on Oct 1, 2014

@author: Sean Mead
"""

from python.modules import Tools


socket_clients = []


def update_clients(code=''):
    """
    Pushes an update to connected clients.
    :param code: Message to send or code to imply.
    """
    clients = []
    for socket in socket_clients:
        try:
            socket.send(Tools.encode_socket(code))
        except Exception:
            clients.append(socket)
    for client in clients:
        try:
            socket_clients.remove(client)
        except Exception:
            pass


def interface():
    var = ''
    while var != 'q':
        var = raw_input('Send: ')
        if var != 'q':
            update_clients(var)