"""
Created on Oct 1, 2014

@author: Sean Mead
"""

from python.modules import Session, Users, SocketClients
from python.site import WebData


def current_user_path(handler):
    """
    Return the full path to the User folder.
    :param handler: the self.__handler of the Links object.
    """
    return Users.USER_PATH + Session.get_name(handler) + '/'


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


class Links(object):
    def __init__(self, handler):
        """
        Create a links object used to handle url paths.
        :param handler: the handler of the client
        """
        self.__handler = handler

    def refresh_script(self):
        if Session.valid(self.__handler):
            return WebData.Script.InnerMenu
        else:
            return WebData.Script.OuterMenu

    def logout(self):
        Session.stop(self.__handler)
        return 'True'

    def register(self):
        if self.__handler.POST:
            username = self.__handler.get_argument('username')
            password = self.__handler.get_argument('password')
            if not Users.exists(username):
                Users.append_user(username, password)
                Session.start(self.__handler, username)
                return 'True'
            return 'False'
        else:
            return Session.valid(self.__handler)

    def login(self):
        if self.__handler.POST:
            username = self.__handler.get_argument('username')
            password = self.__handler.get_argument('password')
            if Users.exists(username):
                if Users.get_password(username) == password:
                    Session.start(self.__handler, username)
                    return 'True'
            return 'False'
        elif Session.valid(self.__handler):
            return WebData.Script.load('Home')
        return False

    def home(self):
        if Session.valid(self.__handler):
            name = Session.get_name(self.__handler)
            return """
                <h2>Hello</h2>
                <div class="center">
                    <section>
                        <p>Welcome %s</p>
                    </section>
                </div>
            """ % name
        return False

    def upload(self):
        if Session.valid(self.__handler):
            if self.__handler.POST:
                if Session.valid(self.__handler):
                    path = current_user_path(self.__handler)
                    self.__handler.move_tmp(path)
                return 'True'
