"""
Created on Jan 30, 2014

@author: Sean Mead
"""


import uuid


SESSIONS = {}

SESSION = 'SESSION'


def start(handler, name):
    sid = str(uuid.uuid4())
    handler.set_cookie(name=SESSION, value=sid)
    SESSIONS.update({sid: name})


def stop(handler):
    if valid(handler):
        SESSIONS.pop(handler.get_cookie(SESSION))


def valid(handler):
    return handler.get_cookie(SESSION) in SESSIONS


def get_name(handler):
    if valid(handler):
        return SESSIONS.get(handler.get_cookie(SESSION))
    return None
