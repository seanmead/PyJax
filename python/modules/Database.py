"""
Created on Jan 30, 2014

@author: Sean Mead
"""


import sqlite3 as sql


class Database(object):
    def __init__(self, path):
        """
        Generic sqlite Database abstraction.
        :param path: The path including the filename of the database.
        """
        self.__conn = sql.connect(path)
        self.__cursor = self.__conn.cursor()

    def create(self, table, items):
        """
        Create a table in the database.
        :param table: Name of the table to create
        :param items: A string list of items to create.  Example: 'username, password'
        """
        self.__cursor.execute("CREATE TABLE %s (%s)" % (table, items))
        self.__conn.commit()

    def update(self, q, param=None):
        """
        Works like a query but isn't intended to return anything.
        :param q: String query
        :param param: String param
        """
        if param:
            self.__cursor.execute(q, param)
        else:
            self.__cursor.execute(q)
        self.__conn.commit()

    def delete(self, q):
        """
        Regular query must specify commands.
        :param q:
        """
        self.__cursor.execute(q)
        self.__conn.commit()

    def query(self, q, param=None):
        """
        Query the database with query and parameters.
        :param q:
        :param param:
        :return:
        """
        try:
            if param:
                self.__cursor.execute(q, param)
            else:
                self.__cursor.execute(q)
            return self.__cursor.fetchall()
        except sql.OperationalError as oe:
            print oe, q

    def headers(self, table):
        """
        Return the headers of a table.
        :param table: The name of the table to retrieve headers on.
        """
        return self.query("PRAGMA table_info(%s)" % table)

    def tables(self):
        """
        Return the tables of the database.
        :return:
        """
        return self.query("SELECT name from sqlite_master WHERE type = 'table'")

    def close(self):
        """
        Close the database.
        """
        self.__cursor.close()
        self.__conn.close()
