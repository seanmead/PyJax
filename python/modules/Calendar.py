__author__ = 'seanmead'

import time


DAY = 86400
HOUR = 3600


class Stamp(object):
    def __init__(self, epoch):
        self.__epoch = int(epoch)
        self.__stamps = time.strftime("%A:%d:%B:%Y:%H:%M:%S", time.localtime(self.__epoch)).split(':')

    @property
    def epoch(self):
        return self.__epoch

    def in_minutes(self):
        return self.epoch / 60

    def in_hours(self):
        return self.epoch / HOUR

    def in_days(self):
        return self.epoch / DAY

    def day_epoch(self):
        return self.in_days() * DAY

    def day(self):
        return self.__stamps[0]

    def date(self):
        return int(self.__stamps[1])

    def month(self):
        return self.__stamps[2]

    def year(self):
        return self.__stamps[3]

    def hour(self):
        return int(self.__stamps[4])

    def minute(self):
        return int(self.__stamps[5])

    def second(self):
        return int(self.__stamps[6])


def compare(stamp1, stamp2):
    return Stamp(abs(stamp1.epoch - stamp2.epoch))


def get_time():
    return int(time.time())


def get_bhours(start, stop, bis_hours=None, weekend=['Saturday', 'Sunday']):
    order = Stamp(start)
    now = Stamp(stop)

    first_day = 0
    if order.day() not in weekend:
        if order.hour() in bis_hours:
            if now.in_days() == order.in_days():
                if now.hour() in bis_hours:
                    first_day = now.hour() - order.hour()
            else:
                first_day = bis_hours[-1] - order.hour()

    hours = 0
    days = (now.epoch - order.epoch) / DAY
    for i in range(0, days):
        day = Stamp(order.day_epoch() + (i * DAY))
        if day.day() not in weekend:
            if now.in_days() == day.in_days():
                if now.hour() in bis_hours:
                    hours += now.hour() - bis_hours[0]
                else:
                    hours += bis_hours[-1] - bis_hours[0]
            else:
                hours += bis_hours[-1] - bis_hours[0]

    return hours + first_day