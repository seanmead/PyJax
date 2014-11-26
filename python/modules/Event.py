__author__ = 'seanmead'


import threading
import time


def human_time(epoch):
    """
    Return a human readable epoch.
    :param epoch:
    """
    return time.strftime("%a, %d %b %Y %I:%M:%S %p", time.localtime(epoch))


def chunks(l, n):
    if n < 1:
        n = 1
    return [l[i:i + n] for i in range(0, len(l), n)]


class Event(threading.Thread):
    __events = {}

    def __init__(self, obj=None, method=None, key=None, interval=None,
                 onetime=False, cleanup=False, responsiveness=1, args=None):
        threading.Thread.__init__(self)
        self.daemon = True
        self.__obj = obj
        self.__method = method
        self.__args = args
        self.__interval = interval
        self.__onetime = onetime
        self.__cleanup = cleanup
        self.__key = key
        self.__last_run = 0
        self.__start_time = 0
        self.__alive = False
        self.__responses = {}
        self.__run_count = 0
        self.__responsiveness = responsiveness

    def __str__(self):
        if self.alive:
            if self.last_run != 0:
                run_time = self.last_run + self.interval - time.time()
            else:
                run_time = self.start_time + self.interval - time.time()
        else:
            run_time = 'Dead'
        return '\n--Event--\nkey: %s\nstarted: %s\nlast run: %s\nalive: %s\nobj: %s\n' \
               'method: %s\nOnetime: %s\ninterval: %s\nNext Run: %s\nRun Count: %s\n--End Event--' % \
               (self.key, human_time(self.start_time), human_time(self.last_run), self.alive, self.obj,
                self.method, self.onetime, self.interval, run_time, self.__run_count)

    @property
    def run_count(self):
        return self.__run_count

    @run_count.setter
    def run_count(self, run_count):
        self.__run_count = run_count

    @property
    def start_time(self):
        return self.__start_time

    @start_time.setter
    def start_time(self, start_time):
        self.__start_time = start_time

    @property
    def responses(self):
        return self.__responses

    @property
    def alive(self):
        return self.__alive

    @alive.setter
    def alive(self, alive):
        self.__alive = alive

    @property
    def last_run(self):
        return self.__last_run

    @last_run.setter
    def last_run(self, run):
        self.__last_run = run

    @property
    def onetime(self):
        return self.__onetime

    @onetime.setter
    def onetime(self, onetime):
        self.__onetime = onetime

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
    def clean():
        keys = []
        for event in Event.__events.values():
            if not event.alive and event.run_count > 0:
                keys.append(event.key)
        Event.remove_events(keys)

    @staticmethod
    def add_event(event=None, obj=None, method=None, key=None,
                  interval=None, onetime=False, cleanup=False, start=False, responsiveness=1,
                  args=None):

        if not event:
            event = Event(obj=obj, method=method, key=key, interval=interval,
                          onetime=onetime, cleanup=cleanup, responsiveness=responsiveness, args=args)
        elif key:
            event.key = key
        Event.__events.update({event.key: event})
        if start:
            event.start()

    @staticmethod
    def remove_event(key, stop=True):
        if key in Event.__events:
            Event.__events.pop(key).alive = not stop

    @staticmethod
    def remove_events(keys, stop=True):
        for key in keys:
            Event.remove_event(key, stop)

    @staticmethod
    def get_event(key):
        return Event.__events.get(key)

    @staticmethod
    def get_events():
        return Event.__events.values()

    @staticmethod
    def stop_event(key):
        if key in Event.__events:
            Event.get_event(key).alive = False

    @staticmethod
    def join_event(key, timeout=10):
        if key in Event.__events:
            Event.get_event(key).join(timeout)

    @staticmethod
    def join_events(keys, timeout=10):
        for key in keys:
            Event.join_event(key, timeout)

    @staticmethod
    def stop_events(keys):
        for key in keys:
            Event.stop_event(key)

    @staticmethod
    def start_event(key):
        if key in Event.__events:
            Event.__events.get(key).start()

    @staticmethod
    def start_events():
        for item in Event.__events.items():
            item[1].start()

    @staticmethod
    def print_event(key):
        if key in Event.__events:
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

    @staticmethod
    def stop_all():
        Event.stop_events(Event.__events.keys())

    @staticmethod
    def join_all(timeout=10):
        keys = Event.__events.keys()
        Event.stop_events(keys)
        kwargs = {'obj': Event, 'method': 'join_events', 'interval': 0, 'onetime': True, 'cleanup': True, 'start': True}
        if len(keys) > 100:
            chunk = chunks(keys, len(keys) / 25)
        else:
            chunk = chunks(keys, 4)
        for key_l in chunk:
            Event.add_event(args={'keys': key_l}, key=str('keys_%s%s' % (key_l[0], time.time())), **kwargs)
        for key in keys:
            Event.join_event(key, timeout)
        for key in Event.__events.keys():
            Event.join_event(key)
        return len(keys)

    @staticmethod
    def hold():
        while True:
            Event.sleep(10)

    @staticmethod
    def sleep(count=1):
        time.sleep(count)

    @staticmethod
    def stack():
        print threading.stack_size()

    def __call(self):
        if self.alive:
            self.last_run = time.time()
            try:
                if self.__args:
                    self.responses.update({self.last_run: getattr(self.obj, self.method)(**self.__args)})
                else:
                    self.responses.update({self.last_run: getattr(self.obj, self.method)()})
                self.run_count += 1
            except Exception as e:
                print e

    def __interrupt_sleep(self):
        for i in range(0, int(self.interval / self.__responsiveness)):
            if not self.alive:
                return
            time.sleep(self.__responsiveness)

    def run(self):
        self.start_time = time.time()
        self.alive = True
        if self.onetime:
            self.__interrupt_sleep()
            self.__call()
        else:
            while self.alive:
                self.__call()
                self.__interrupt_sleep()
        if self.__cleanup:
            Event.remove_event(self.key)