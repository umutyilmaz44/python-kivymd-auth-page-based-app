import os
import hashlib
from db_utilities.repositories.database import Database
from db_utilities.repositories.db_exception import DbException

class UserRepository():

    def __init__(self, database):       
        self.db = database

    def tuple_to_dict(self, mytuple):
        mydict = dict()
        mydict['id'] = mytuple[0]
        mydict['username'] = mytuple[1]
        mydict['fullname'] = mytuple[2]
        mydict['password'] = mytuple[3]
        mydict['userRole'] = mytuple[4]
        return mydict
        
    def insert(self, user):
        try:
            c = self.db.conn.cursor()
            # this needs an appropriate table
            c.execute("INSERT INTO user ('username','fullname','password','userRole') VALUES(?, ?, ?, ?)", (user.username, user.fullname, user.password, user.userRole))
            self.db.conn.commit()
        except Exception as e:
            raise DbException(*e.args, **e.kwargs)
    
    def insert_list(self, users):
        try:
            entries = list()
            for x in users:
                entries.append((x['username'], x['fullname'], x['password'], x['userRole']))
            c = self.conn.cursor()
            # this needs an appropriate table
            c.execute("INSERT INTO user ('username','fullname','password','userRole') VALUES(?, ?, ?, ?)", entries)
            self.conn.commit()
        except Exception as e:
            raise DbException(*e.args, **e.kwargs)
    
    def find_by_condition(self, condition=None, order=None, limit=None):
        try:
            c = self.db.conn.cursor()
            # this needs an appropriate table
            sql= ""
            if(condition is None or condition == ""):
                sql= "SELECT * FROM user"
            else :
                sql= "SELECT * FROM user WHERE " + condition

            if(order is not None and len(order) > 0):
                sql= sql + " ORDER BY " + order

            if(limit is not None and len(str(limit)) > 0):
                sql= sql + " LIMIT " + str(limit)

            c.execute(sql)
            results = c.fetchall()
            return list(map(lambda x: self.tuple_to_dict(x), results))
        except Exception as e:
            raise DbException(*e.args, **e.kwargs)
    
    def update(self, user):        
        sql_check = 'SELECT EXISTS(SELECT 1 FROM user WHERE id=? LIMIT 1)'
        sql_update = 'UPDATE user SET username=?, fullname=?, password=?, userRole=? WHERE id=?'
        c = self.db.conn.execute(sql_check, (user.id,))  # we need the comma
        result = c.fetchone()
        if result[0]:
            c.execute(sql_update, (user.username, user.fullname, user.password, user.userRole, user.id))
            self.db.conn.commit()
        else:
            raise DbException("Can't update user (id:{}) because it's not stored in db".format(user.id,))

    def updateWithoutPassword(self, user):        
        sql_check = 'SELECT EXISTS(SELECT 1 FROM user WHERE id=? LIMIT 1)'
        sql_update = 'UPDATE user SET username=?, fullname=?, userRole=? WHERE id=?'
        c = self.db.conn.execute(sql_check, (user.id,))  # we need the comma
        result = c.fetchone()
        if result[0]:
            c.execute(sql_update, (user.username, user.fullname, user.userRole, user.id))
            self.db.conn.commit()
        else:
            raise DbException("Can't update user (id:{}) because it's not stored in db".format(user.id,))
    
    def delete(self, user):        
        sql_check = 'SELECT EXISTS(SELECT 1 FROM user WHERE id=? LIMIT 1)'
        sql_delete = 'DELETE FROM user WHERE id=?'
        c = self.db.conn.execute(sql_check, (user.id,))  # we need the comma
        result = c.fetchone()
        if result[0]:
            c.execute(sql_delete, (user.id,))  # we need the comma
            self.db.conn.commit()
        else:
            raise DbException("Can't delete user (id:{}) because it's not stored in db".format(user.id,))

    def deleteById(self, id):
        sql_check = 'SELECT EXISTS(SELECT 1 FROM user WHERE id=? LIMIT 1)'
        sql_delete = 'DELETE FROM user WHERE id=?'.format(id,)
        c = self.db.conn.execute(sql_check, (id,))  # we need the comma
        result = c.fetchone()
        if result[0]:
            c.execute(sql_delete, (id,))  # we need the comma
            self.db.conn.commit()
        else:
            raise DbException("Can't delete user (id:{}) because it's not stored in db".format(id,))

    def get_hash(self, salt, password):
        if(password == None or len(password) == 0):
            return None

        if(salt == None or len(salt) == 0):
            salt = os.urandom(32)

        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        storage = salt + key 

        return storage
    
    def get_hash_parts(self, storage):
        salt = storage[:32] # 32 is the length of the salt
        hashedPassword = storage[32:]
        return salt, hashedPassword