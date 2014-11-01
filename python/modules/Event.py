__author__ = 'seanmead'


import threading
import time


class Event(threading.Thread):
    __events = {}

    def __init__(self, obj=None, method=None, interval=None, key=None):
        threading.Thread.__init__(self)
        self.daemon = True
        self.__obj = obj
        self.__method = method
        self.__interval = interval
        self.__key = key
        self.__last_run = 0

    def __str__(self):
        return '\n--Event--\nkey: %s\nobj: %s\nmethod: %s\ninterval: %s\nNext Run: %s\n--End Event--' % \
               (self.key, self.obj, self.method, self.interval, self.last_run + self.interval - time.time())

    @property
    def last_run(self):
        return self.__last_run

    @last_run.setter
    def last_run(self, run):
        self.__last_run = run

    @property
    def obj(self):
        return self.__obj

    @obj.setter
    def obj(self, obj):
        self.__obj = obj

    @property
    def method(self):
        return self.__method

    @method.setter
    def method(self, method):
        self.__method = method

    @property
    def interval(self):
        return self.__interval

    @interval.setter
    def interval(self, interval):
        self.__interval = interval

    @property
    def key(self):
        return self.__key

    @key.setter
    def key(self, key):
        self.__key = key

    @staticmethod
    def add_event(event, key=None):
        if key:
            event.key = key
        Event.__events.update({event.key: event})

    @staticmethod
    def remove_event(key):
        Event.__events.pop(key)

    @staticmethod
    def get_event(key):
        return Event.__events.get(key)

    @staticmethod
    def start_event(key):
        Event.__events.get(key).start()

    @staticmethod
    def start_events():
        for item in Event.__events.items():
            item[1].start()

    @staticmethod
    def print_event(key):
        print Event.__events.get(key)

    @staticmethod
    def print_events():
        print '\n\n----Events----'
        for item in Event.__events.values():
            print item
        print '\n----End Events----\n\n'

    @staticmethod
    def minutes(minutes):
        return minutes * 60

    @staticmethod
    def hours(hours):
        return Event.minutes(hours) * 60

    def run(self):
        while self.isAlive():
            self.last_run = time.time()
            try:
                getattr(self.__obj, self.__method)()
            except Exception as e:
                print e
            time.sleep(self.__interval)
