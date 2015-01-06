# -*- coding: cp936 -*-
import sqlite3
import datetime
import gl

def sqlitePool(db="carrecgser.db",maxu=1000):
    gl.sqlitepool = PersistentDB(
        sqlite3,
        maxusage = maxu,
        database = db)
    
class U_Sqlite:
    def __init__(self):
        #self.conn = gl.sqlitepool.connection(check_same_thread = False)
        #self.cur  = self.conn.cursor()
        self.conn = sqlite3.connect("carrecgser.db",check_same_thread = False)
        self.cur  = self.conn.cursor()
            
    def __del__(self):
        try:
            self.conn.close()
            self.cur.close()
        except Exception,e:
            pass

    def createTable(self):
        sql = '''CREATE TABLE IF NOT EXISTS "uploadsys" (
                "id"  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                "year"  INTEGER NOT NULL DEFAULT 2014,
                "month"  INTEGER NOT NULL DEFAULT 1,
                "day"  INTEGER NOT NULL DEFAULT 1,
                "hour"  INTEGER NOT NULL DEFAULT 0
                );
                '''

        self.cur.executescript(sql)
        self.conn.commit()
        if self.getUploadsys() == None:
            now = datetime.datetime.now()
            self.cur.execute("INSERT INTO uploadsys (id,year,month,day,hour) VALUES(1,%s,%s,%s,%s)"%(now.year,now.month,now.day,0))
            self.conn.commit()

    #获取数据上传状态记录
    def getUploadsys(self):
        try:
            self.cur.execute("select * from uploadsys where id=1")
            s = self.cur.fetchone()
        except sqlite3.Error as e:
            raise
        else:
            self.conn.commit()
            return s

    #获取用户信息
    def get_users(self):
        try:
            self.cur.execute("select * from user")
            s = self.cur.fetchall()
            self.conn.commit()
            return s
        except sqlite3.Error as e:
            raise

    #更新数据上传状态记录
    def get_user_by_key(self,key):
        try:
            self.cur.execute("select * from user where key='%s'"%key)
            s = self.cur.fetchone()
            self.conn.commit()
            return s
        except sqlite3.Error as e:
            raise
        
    def endOfCur(self):
        self.conn.commit()
        
    def sqlCommit(self):
        self.conn.commit()
        
    def sqlRollback(self):
        self.conn.rollback()
            
if __name__ == "__main__":
    #from DBUtils.PersistentDB import PersistentDB
    #import gl
    #sqlitePool()
    sl = U_Sqlite()
    print sl.get_user_by_key('keys')

    del sl


