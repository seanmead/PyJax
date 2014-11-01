from python.modules.Server import Server, WebSocketServer
from python.modules import Tools
from python.modules import Settings

__author__ = 'Sean Mead'


class Static(type):
    """
    Holds the servers as static variables
    """
    web = Server()
    sock = WebSocketServer()


def start():
    """
    Start the servers
    """
    Static.sock.start()
    Static.web.start()
    print '\t**PyJax**\n'
    print '%s:%s' % (Settings.get('address'), Settings.get('port'))


if __name__ == "__main__":
    Tools.clear_screen()
    var = ''
    try:
        start()
        while var != 'q':
            var = raw_input('Enter \'q\' to quit or \'r\' to restart: ')
    except Exception as e:
        print 'Error: %s' % e