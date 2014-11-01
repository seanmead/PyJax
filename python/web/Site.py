"""
Created on Oct 1, 2014

@author: Sean Mead
"""

from python.modules import Session
from python.web import Users
from python.web import SocketClients


KEY = "KEY"


def current_user_path(handler):
    """
    Return the full path to the User folder.
    :param handler: the self.__handler of the Links object.
    """
    return Users.USER_PATH + Session.get_name(handler) + '/'


class Links(object):
    def __init__(self, handler):
        """
        Create a links object used to handle url paths.
        :param handler: the handler of the client
        """
        self.__handler = handler

    def logout(self):
        if self.__handler.req.method == "POST":
            try:
                SocketClients.socket_clients.remove(self.__handler.connection)
            except Exception:
                pass
            Session.stop(self.__handler)
            return 'True'

    def register(self):
        if self.__handler.req.method == "POST":
            username = self.__handler.get_argument('username')
            password = self.__handler.get_argument('password')
            key = self.__handler.get_argument('key')
            if key == KEY:
                if not Users.exists(username):
                    Users.append_user(username, password)
                    Session.start(self.__handler, username)
                    return 'True'
            return 'False'

    def login(self):
        if self.__handler.req.method == "POST":
            username = self.__handler.get_argument('username')
            password = self.__handler.get_argument('password')
            if Users.exists(username):
                if Users.get_password(username) == password:
                    Session.start(self.__handler, username)
                    return 'True'
            return 'False'
        return False

    def stream_do_upload(self):
        if Session.valid(self.__handler):
            path = current_user_path(self.__handler)
            filename = self.__handler.move_tmp(path)
        return 'True'


class Socket(object):
    def __init__(self, handler):
        """
        The socket object creates links used by the client's socket connection.
        :param handler: the handler of the client
        """
        self.__handler = handler

    def validate(self):
        """
        Validate appends the clients connection to the known connections list.
        :return:
        """
        if Session.valid(self.__handler):
            SocketClients.socket_clients.append(self.__handler.connection)
            return 'True'
