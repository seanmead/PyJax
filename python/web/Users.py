"""
Created on Oct 1, 2014

@author: Sean Mead
"""

from python.modules.Database import Database
from python.modules.Settings import Settings
import os


DB_PATH = Settings.DB_DIR + 'Users.db'
USER_PATH = Settings.USER_DIR
TABLE_USERS = "users"
TABLE_QUEUES = "queues"


def create_users():
    """
    Create the users folder.
    """
    if not os.path.isdir(USER_PATH):
        os.mkdir(USER_PATH)


def create_database():
    """
    Create the users database.
    """
    db = Database(DB_PATH)
    try:
        db.create(TABLE_QUEUES, 'username, name')
    except Exception:
        pass
    try:
        db.create(TABLE_USERS, 'username, password')
    except Exception:
        pass
    db.close()


def append_user(username, password):
    """
    Adds a user to the database and creates their user folder.
    :param username: Name of the user
    :param password: Password for the account, should be hashed.
    """
    db = Database(DB_PATH)
    db.update('INSERT INTO %s VALUES(?, ?);' % TABLE_USERS, (username, password))
    db.close()
    os.mkdir(USER_PATH + username)


def get_password(username):
    """
    Returns the password for a given username.
    :param username: Name of the user
    :return: The password
    """
    db = Database(DB_PATH)
    password = db.query("SELECT password FROM %s WHERE username=?;" % TABLE_USERS, (username, ))[0][0]
    db.close()
    return password


def exists(username):
    """
    Checks if the user exists.
    :param username: Name of the user
    :return: Boolean value, True if the user exists.
    """
    db = Database(DB_PATH)
    num = db.query("SELECT COUNT(*) as count FROM %s WHERE username=?;" % TABLE_USERS, (username, ))[0][0]
    db.close()
    return num > 0


def get_queues(username):
    """
    Query the queues for a given username.
    :param username: Name of the user
    :return: A list of queues
    """
    db = Database(DB_PATH)
    queues = []
    try:
        query = db.query("SELECT NAME FROM %s WHERE username=?;" % TABLE_QUEUES, (username, ))
        for item in query:
            queues.append(item[0])
    except Exception:
        pass
    db.close()
    return queues


def append_queue(username, queue):
    """
    Add a queue for the given username.
    :param username: Name of the user
    :param queue: Name of queue to add
    """
    db = Database(DB_PATH)
    db.update('INSERT OR REPLACE INTO %s VALUES(?, ?);' % TABLE_QUEUES, (username, queue))
    db.close()


def delete_queue(username, queue):
    """
    Delete a queue for a given user.
    :param username: Name of the user
    :param queue: Name of the queue to delete
    """
    db = Database(DB_PATH)
    db.update('DELETE FROM %s WHERE username=? and name=?' % TABLE_QUEUES, (username, queue))


create_database()
create_users()

