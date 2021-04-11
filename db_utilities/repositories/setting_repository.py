from db_utilities.repositories.database import Database
from db_utilities.repositories.db_exception import DbException
from db_utilities.models.setting import Setting

class SettingRepository():

    def __init__(self, database):       
        self.db = database

    def tuple_to_dict(self, mytuple):
        mydict = dict()
        mydict['id'] = mytuple[0]
        mydict['setting_key'] = mytuple[1]
        mydict['setting_value'] = mytuple[2]

        return mydict
        
    def insert(self, setting:Setting):
        try:
            c = self.db.conn.cursor()
            # this needs an appropriate table
            c.execute("INSERT INTO setting ('setting_key','setting_value') VALUES(?, ?)", 
                    (setting.setting_key, setting.setting_value))
            self.db.conn.commit()
        except Exception as e:
            raise DbException(*e.args, **e.kwargs)
    
    def insert_list(self, settings):
        try:
            entries = list()
            for x in settings:
                entries.append((x['setting_key'], x['setting_value']))
            c = self.conn.cursor()
            # this needs an appropriate table
            c.execute("INSERT INTO setting ('setting_key','setting_value') VALUES(?, ?)", entries)
            self.conn.commit()
        except Exception as e:
            raise DbException(*e.args, **e.kwargs)
    
    def find_by_condition(self, condition=None, order=None, limit=None):
        try:
            c = self.db.conn.cursor()
            # this needs an appropriate table
            sql= ""
            if(condition is None or condition == ""):
                sql= "SELECT * FROM setting"
            else :
                sql= "SELECT * FROM setting WHERE " + condition
            
            if(order is not None and len(order) > 0):
                sql= sql + " ORDER BY " + order

            if(limit is not None and len(str(limit)) > 0):
                sql= sql + " LIMIT " + str(limit)

            c.execute(sql)
            results = c.fetchall()
            return list(map(lambda x: self.tuple_to_dict(x), results))
        except Exception as e:
            raise DbException(*e.args, **e.kwargs)
    
    def update(self, setting):        
        sql_check = 'SELECT EXISTS(SELECT 1 FROM setting WHERE id=? LIMIT 1)'
        sql_update = 'UPDATE setting SET '\
                        'setting_key=?, setting_value=? '\
                     'WHERE id=?'
        c = self.db.conn.execute(sql_check, (setting.id,))  # we need the comma
        result = c.fetchone()
        if result[0]:
            c.execute(sql_update, (setting.setting_key, setting.setting_value, setting.id,))
            self.db.conn.commit()
        else:
            raise DbException("Can't update setting (id:{}) because it's not stored in db".format(setting.id,))
    
    def delete(self, setting):        
        sql_check = 'SELECT EXISTS(SELECT 1 FROM setting WHERE id=? LIMIT 1)'
        sql_delete = 'DELETE FROM setting WHERE id=?'
        c = self.db.conn.execute(sql_check, (setting.id,))  # we need the comma
        result = c.fetchone()
        if result[0]:
            c.execute(sql_delete, (setting.id,))  # we need the comma
            self.db.conn.commit()
        else:
            raise DbException("Can't delete setting (id:{}) because it's not stored in db".format(setting.id,))
        
    def deleteById(self, id):
        sql_check = 'SELECT EXISTS(SELECT 1 FROM setting WHERE id=? LIMIT 1)'
        sql_delete = 'DELETE FROM setting WHERE id=?'.format(id,)
        c = self.db.conn.execute(sql_check, (id,))  # we need the comma
        result = c.fetchone()
        if result[0]:
            c.execute(sql_delete, (id,))  # we need the comma
            self.db.conn.commit()
        else:
            raise DbException("Can't delete setting (id:{}) because it's not stored in db".format(id,))
