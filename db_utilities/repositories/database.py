from sqlite3 import OperationalError, IntegrityError, ProgrammingError
from time import *
import sqlite3
from db_utilities.repositories.db_exception import DbException
from sqlite3.dbapi2 import Connection


class Database():
    db_name = 'database'

    def get_connection(self):
        db = '{}.db'.format(self.db_name)
        print('New connection to SQLite DB...')
        connection = sqlite3.connect(db)
        return connection

    def __init__(self):
        try:
            self.conn = self.get_connection()
        except Exception as e:
            print("Connection Error Occured!")
            print(*e.args)
            # raise DbException(*e.args, **e.kwargs)
        self._complete = False

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        # can test for type and handle different situations
        self.close()

    def complete(self):
        self._complete = True

    def close(self):
        if self.conn:
            try:
                if self._complete:
                    self.conn.commit()
                else:
                    self.conn.rollback()
            except Exception as e:
                raise DbException(*e.args)
            finally:
                try:
                    self.conn.close()
                except Exception as e:
                    raise DbException(*e.args)

    def scrub(self, input_string):
        """Clean an input string (to prevent SQL injection).

        Parameters
        ----------
        input_string : str

        Returns
        -------
        str
        """
        return ''.join(k for k in input_string if k.isalnum())

    def create_table(self, table_name):
        sql = ''
        table_name = self.scrub(table_name)
        if table_name == 'user':
            sql = 'CREATE TABLE IF NOT EXISTS {} ('\
                    'id INTEGER PRIMARY KEY AUTOINCREMENT,' \
                    'username TEXT UNIQUE, ' \
                    'fullname TEXT, ' \
                    'password TEXT, ' \
                    'userRole TEXT)'.format(table_name)
        
        elif table_name == 'session':
            sql = 'CREATE TABLE IF NOT EXISTS  {} (' \
                    'id INTEGER PRIMARY KEY AUTOINCREMENT,' \
                    'userid INTEGER NOT NULL, ' \
                    'loginTime timestamp NOT NULL, ' \
                    'logoutTime timestamp)'.format(table_name)
                    
        elif table_name == 'setting':
            sql = 'CREATE TABLE IF NOT EXISTS  {} (' \
                    'id INTEGER PRIMARY KEY AUTOINCREMENT,' \
                    'setting_key TEXT, ' \
                    'setting_value TEXT)'.format(table_name)
                    
        try:
            self.conn.execute(sql)
        except OperationalError as e:
            raise DbException(*e.args)

    def initialize_db(self):
        self.create_table("user")
        self.create_table("session")
        self.create_table("setting")
        
