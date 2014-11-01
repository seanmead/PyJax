"""
Created on Oct 1, 2014

@author: Sean Mead
"""

import os
import Tools


def get_files(path, ext):
    return [f for f in os.listdir(path) if
            os.path.isfile(os.path.join(path, f)) and f.endswith(ext) and not f.startswith('.')]


def split_extension(filename):
    name, ext = os.path.splitext(filename)
    ext = ext.replace(".", "")
    return name, ext


def read_file(path):
    with open(path, 'rb') as h:
        f = h.read()
    return f


class Settings(object):
    WORKING_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/../') + '/'
    CONFIG_DIR = WORKING_DIR + 'config/'
    FRAMEWORK_DIR = WORKING_DIR + 'framework/'
    SCRIPT_DIR = FRAMEWORK_DIR + 'scripts/'
    WEB_DIR = WORKING_DIR + 'web/'
    ASSET_DIR = WEB_DIR + 'assets/'
    CERT_DIR = WORKING_DIR + 'certs/'
    DB_DIR = WORKING_DIR + 'database/'
    USER_DIR = WORKING_DIR + 'users/'
    CACHE_DIR = WORKING_DIR + 'cache/'

    def __init__(self):
        self.__config = Settings._read_config()
        self.__config.update(Settings._read_meta())
        self.__config.update(Settings._read_ico())
        self.__config.update(Settings._read_jquery())
        self.__config.update(Settings._read_smart(home=self.__config.get('home')))
        self.__config.update(Settings._read_frame())
        self.__config.update(Settings._read_nav(title=self.__config.get('title')))
        self.__config.update(Settings._read_footer())
        self.__config.update(Settings._read_html())
        self.__config.update(Settings._read_style())
        self.__config.update(Settings._read_images())
        self.__config.update(self._read_javascript())
        self.__config.update(Settings._read_media())
        self.__config.update(Settings._read_404())
        self.__config.update(Settings._read_cert())

    @property
    def config(self):
        return self.__config

    @config.getter
    def config(self):
        return self.__config

    @staticmethod
    def _read_config():
        config = read_file(Settings.CONFIG_DIR + 'config.txt')
        configs = {}
        for line in config.split('\n'):
            name, value = line.split('=', 2)
            name = name.strip()
            value = value.strip()
            if name == 'address':
                if value == 'auto':
                    value = Tools.get_address()
            if 'port' in name:
                value = int(value)
            configs.update({name: value})
        return configs

    @staticmethod
    def _read_meta():
        return {'meta': read_file(Settings.CONFIG_DIR + 'meta.html')}

    @staticmethod
    def _read_ico():
        return {'ico': read_file(Settings.CONFIG_DIR + 'icon.html')}

    @staticmethod
    def _read_jquery():
        return {'jquery': read_file(Settings.SCRIPT_DIR + 'jquery.min.js')}

    @staticmethod
    def _read_smart(home):
        smart = read_file(Settings.SCRIPT_DIR + 'smartnav.js')
        smart_insert = read_file(Settings.SCRIPT_DIR + 'smartnav-insert.js')
        smart = smart.replace('//<!--INSERT-->', smart_insert)
        smart = smart.replace('<inject-home>', home)
        return {'smart': smart}

    @staticmethod
    def _read_404():
        return {'404': read_file(Settings.FRAMEWORK_DIR + '404.html')}

    @staticmethod
    def _read_frame():
        return {'frame': read_file(Settings.FRAMEWORK_DIR + 'frame.html')}

    @staticmethod
    def _read_nav(title):
        nav = read_file(Settings.FRAMEWORK_DIR + 'nav.html')
        nav_options = read_file(Settings.FRAMEWORK_DIR + 'nav-options.html')
        link_h = open(Settings.CONFIG_DIR + 'links.txt', 'r')
        links = link_h.readlines()
        link_h.close()
        links_format = ''
        for link in links:
            link = link.strip()
            links_format += '<a href="#" id="%s" %s >%s</a>' % (link, nav_options, link)

        nav = nav.replace('<!--LINKER-->', links_format)
        nav = nav.replace('<!--TITLE-->', title)
        nav = nav.replace('<!--DONT REMOVE THE LINKER COMMENT-->', '')
        nav = nav.replace('<!--It is going to be replaced by the nav links-->', '')
        return {'nav': nav}

    @staticmethod
    def _read_footer():
        return {'footer': read_file(Settings.FRAMEWORK_DIR + 'footer.html')}

    @staticmethod
    def _read_html():
        files = get_files(Settings.WEB_DIR, 'html')
        pages = {}
        for item in files:
            name, ext = split_extension(item)
            pages.update({name: read_file(Settings.WEB_DIR + item)})
        return {'pages': pages}

    @staticmethod
    def _read_style():
        style = {}
        files = get_files(Settings.ASSET_DIR + 'css/', 'css')
        for item in files:
            style.update({item: read_file(Settings.ASSET_DIR + 'css/' + item)})
        return {'style': style}

    @staticmethod
    def _read_images():
        files = get_files(Settings.ASSET_DIR + 'img/', '')
        images = {}
        for item in files:
            images.update({item: Settings.ASSET_DIR + 'img/' + item})
        return {'img': images}

    def _read_javascript(self):
        files = get_files(Settings.ASSET_DIR + 'js/', 'js')
        javascript = {}
        for item in files:
            js = read_file(Settings.ASSET_DIR + 'js/' + item)
            for sets in self.config:
                val = str(self.config.get(sets))
                name = str(sets)
                js = js.replace('<inject-%s>' % name, val)
            javascript.update({item: js})
        return {'js': javascript}

    @staticmethod
    def _read_media():
        files = get_files(Settings.ASSET_DIR + 'media/', '')
        media = {}
        for item in files:
            media.update({item: Settings.ASSET_DIR + 'media/' + item})
        return {'media': media}

    @staticmethod
    def _read_cert():
        try:
            return {'cert': Settings.CERT_DIR + get_files(Settings.CERT_DIR, 'pem')[0]}
        except Exception:
            return {'cert': None}


class Static(type):
    settings = Settings()


def reset():
    Static.settings = Settings()


def get_settings():
    return Static.settings


def get(param):
    if param in Static.settings.config:
        return Static.settings.config.get(param)