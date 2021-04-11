from db_utilities.repositories.database import Database
from db_utilities.repositories.db_exception import DbException

class SessionRepository():

    def __init__(self, database):       
        self.db = database

    def tuple_to_dict(self, mytuple):
        mydict = dict()
        mydict['id'] = mytuple[0]
        mydict['userid'] = mytuple[1]
        mydict['loginTime'] = mytuple[2]
        mydict['logoutTime'] = mytuple[3]
        return mydict
        
    def insert(self, session):
        try:
            c = self.db.conn.cursor()
            # this needs an appropriate table
            c.execute("INSERT INTO session ('userid','loginTime','logoutTime') VALUES(?, ?, ?)", (session.userid, session.loginTime, session.logoutTime))
            self.db.conn.commit()
        except Exception as e:
            raise DbException(*e.args, **e.kwargs)
    
    def insert_list(self, sessions):
        try:
            entries = list()
            for x in sessions:
                entries.append((x['userid'], x['loginTime'], x['logoutTime']))
            c = self.conn.cursor()
            # this needs an appropriate table
            c.execute("INSERT INTO session ('userid','loginTime','logoutTime') VALUES(?, ?, ?)", entries)
            self.conn.commit()
        except Exception as e:
            raise DbException(*e.args, **e.kwargs)
    
    def find_by_condition(self, condition=None, order=None, limit=None):
        try:
            c = self.db.conn.cursor()
            # this needs an appropriate table
            sql= ""
            if(condition is None or condition == ""):
                sql= "SELECT * FROM session"
            else :
                sql= "SELECT * FROM session WHERE " + condition

            if(order is not None and len(order) > 0):
                sql= sql + " ORDER BY " + order

            if(limit is not None and len(str(limit)) > 0):
                sql= sql + " LIMIT " + str(limit)

            c.execute(sql)
            results = c.fetchall()
            return list(map(lambda x: self.tuple_to_dict(x), results))
        except Exception as e:
            raise DbException(*e.args, **e.kwargs)
    
    def update(self, session):        
        sql_check = 'SELECT EXISTS(SELECT 1 FROM session WHERE id=? LIMIT 1)'
        sql_update = 'UPDATE session SET userid=?, loginTime=?, logoutTime=? WHERE id=?'
        c = self.db.conn.execute(sql_check, (session.id,))  # we need the comma
        result = c.fetchone()
        if result[0]:
            c.execute(sql_update, (session.userid, session.loginTime, session.logoutTime, session.id))
            self.db.conn.commit()
        else:
            raise DbException("Can't update session (id:{}) because it's not stored in db".format(session.id,))
    
    def delete(self, session):        
        sql_check = 'SELECT EXISTS(SELECT 1 FROM session WHERE id=? LIMIT 1)'
        sql_delete = 'DELETE FROM session WHERE id=?'
        c = self.db.conn.execute(sql_check, (session.id,))  # we need the comma
        result = c.fetchone()
        if result[0]:
            c.execute(sql_delete, (session.id,))  # we need the comma
            self.db.conn.commit()
        else:
            raise DbException("Can't delete session (id:{}) because it's not stored in db".format(session.id,))

    def deleteById(self, id):
        sql_check = 'SELECT EXISTS(SELECT 1 FROM session WHERE id=? LIMIT 1)'
        sql_delete = 'DELETE FROM session WHERE id=?'.format(id,)
        c = self.db.conn.execute(sql_check, (id,))  # we need the comma
        result = c.fetchone()
        if result[0]:
            c.execute(sql_delete, (id,))  # we need the comma
            self.db.conn.commit()
        else:
            raise DbException("Can't delete session (id:{}) because it's not stored in db".format(id,))