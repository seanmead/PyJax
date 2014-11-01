"""
Created on Jan 30, 2014

@author: Sean Mead
"""


from python.web.Site import Links, Socket
from python.modules import Settings, Coder
from python.modules.Media import TYPES


class Builder(object):
    def __init__(self):
        """
        Create a Builder object

        """
        self.__pages = Settings.get('pages')
        self.__jquery = '<script>%s</script>' % Settings.get('jquery')
        self.__smart = '<script>%s</script>' % Settings.get('smart')
        self.__media = Settings.get('media')
        self.__images = Settings.get('img')
        self.__script = Settings.get('js')
        self.__style = Settings.get('style')
        self.__title = Settings.get('title')
        self.__header = '<head>' + Settings.get('meta') + self._get_title() + self._get_style_links() + '</head>'
        self.__body = '<body>' + Settings.get('nav') + Settings.get('frame') + Settings.get('footer') + \
                      self.__jquery + self.__smart + self._get_script_links() + '</body>'

    def _get_title(self):
        """
        Return the html formatted title.
        :return:
        """
        return '<title>%s</title>' % self.__title

    def _get_script_links(self):
        """
        Return the html formatted javascript.
        """
        links = []
        for item in self.__script:
            links.append('<script>%s</script>' % Settings.get('js').get(item))
        return ''.join(links)

    def _get_style_links(self):
        """
        Return the html formatted stylesheet.
        :return:
        """
        links = []
        for item in self.__style:
            links.append('<style>%s</style>' % Settings.get('style').get(item))
        return ''.join(links)

    def find_page(self, name):
        """
        Return the request html page if found.
        """
        name = name.replace('/', '')
        if name in self.__pages:
            return Settings.get('pages')[name]
        return False

    def find_asset(self, asset):
        """
        Return a list containing the Header, and the Asset string.
        :param asset:
        :return:
        :rtype : list
        """
        asset = asset.replace('/', '')
        name, ext = Settings.split_extension(asset)
        if ext:
            if ext == 'js':
                return None, Settings.get('js')[asset]
            elif ext == 'css':
                return None, Settings.get('style').get(asset)
            elif ext in TYPES:
                return self._get_other_asset(asset, ext)
        else:
            if asset == 'jquery':
                return Header('Content-Type', 'text/javascript'), Settings.get('jquery')
            elif asset == 'smart':
                return Header('Content-Type', 'text/javascript'), Settings.get('smart')
        return Header.void(), Settings.get('404')

    def _get_other_asset(self, asset, ext):
        """
        Return asset specifying the extension.
        :param asset:
        :param ext:
        :return:
        """
        header = Header('Content-Type', '%s/%s' % (TYPES.get(ext), ext))
        f = None
        if asset in self.__media:
            f = Settings.read_file(Settings.get('media')[asset])
        elif asset in self.__images:
            f = Settings.read_file(Settings.get('img')[asset])
        return header, f

    def get_document(self, content=None, script=None):
        """
        Return the entire html document with optional injected content.
        :param content:
        :return:
        """
        page = "<!DOCTYPE html><html>" + self.__header + self.__body + "</html>"
        if content:
            page = page.replace('<div id="main">', '<div id="main">' + Coder.decode(content))
        if script:
            page = page.replace('</body>', Coder.decode(script) + '</body>')
        return page


class Header(object):
    def __init__(self, name, value):
        """
        Create a header object with name, value
        :param name:
        :param value:
        :rtype : Header
        """
        self.__name = name
        self.__value = value

    @property
    def name(self):
        return self.__name

    @property
    def value(self):
        """
        Return the value of the header.
        """
        return self.__value

    @staticmethod
    def basic():
        """
        Return a default text/html header.
        :rtype : Header
        """
        return Header('Content-Type', 'text/html')

    @staticmethod
    def void():
        """
        Return an empty header.
        :rtype : Header
        """
        return Header('', '')


builder = Builder()


class Client(object):
    def __init__(self, handler):
        """
        Create a client object.  Requires the Server.Handler object.
        :param handler:
        """
        self.__handler = handler
        self.__links = Links(self.__handler)
        self.__out_headers = []
        self.__path = self.__handler.req.path

    def _send_all(self, content):
        """
        Write all content including the given html content and headers.
        This sends the content to the User.
        :param content:
        """
        for header in self.__out_headers:
            if header:
                self.__handler.set_header(name=header.name, value=header.value)
        self.__handler.write(content)

    def socket(self):
        """
        Initiate the socket connection by injecting WebSocket connection scripts.
        """
        request = self.__path.replace('/', '_')[1:].lower()
        sock = Socket(self.__handler)
        if request in dir(sock):
            self._send_all(getattr(sock, request)())

    def direct(self, message):
        """
        Direct will return the direct content produced by the Web.Socket.
        """
        request = message.replace('/', '_').lower()
        sock = Socket(self.__handler)
        if request in dir(sock):
            return getattr(sock, request)()

    def get(self):
        """
        Forward the get request through the content builders and asset handlers.
        """
        if self.__path != '/':
            build = not 'ajax' in self.__handler.req.arguments
            request = self.__path[1:].replace('/', '_').lower()
            if request in dir(self.__links):
                content = getattr(self.__links, request)()
                if not content:
                    content = builder.find_page(self.__path)
            else:
                content = builder.find_page(self.__path)
            if content or content == "":
                if build:
                    content = builder.get_document(content=content)
            else:
                header, content = builder.find_asset(self.__path)
                self.__out_headers.append(header)
        else:
            content = builder.get_document()
        self._send_all(content)

    def post(self):
        """
        Forward the post request through the content builders and asset handlers.
        """
        if self.__path != '/':
            request = self.__path[1:].replace('/', '_').lower()
            if request in dir(self.__links):
                content = getattr(self.__links, request)()
                if not content:
                    content = builder.find_page(self.__path)
            else:
                content = builder.find_page(self.__path)
            self._send_all(content)
