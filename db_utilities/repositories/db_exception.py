from sqlite3 import OperationalError, IntegrityError, ProgrammingError

class DbException(Exception):
    def __init__(self, message, *errors):
        Exception.__init__(self, message)
        self.errors = errors