# -*- coding: utf-8 -*-
import sqlite3


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class RSqlite:

    def __init__(self):
        self.conn = sqlite3.connect("carrecgser.db", check_same_thread=False)
        self.conn.row_factory = dict_factory
        self.cur = self.conn.cursor()

    def __del__(self):
        try:
            self.conn.close()
            self.cur.close()
        except Exception:
            pass

    def create_table(self):
        sql = '''CREATE TABLE IF NOT EXISTS "user" (
                "id"  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                "key"  TEXT,
                "priority"  INTEGER NOT NULL DEFAULT 10,
                "multiple"  INTEGER NOT NULL DEFAULT 2,
                "mark"  TEXT
                );

                CREATE UNIQUE INDEX IF NOT EXISTS "idx_key"
                ON "user" ("key" ASC);
                '''

        self.cur.executescript(sql)
        self.conn.commit()

    def get_users(self):
        """获取用户信息"""
        try:
            self.cur.execute("SELECT * FROM user")
            s = self.cur.fetchall()
            self.conn.commit()
            return s
        except sqlite3.Error:
            raise

    def get_user_by_key(self, key):
        """根据KEY获取用户信息"""
        try:
            self.cur.execute("SELECT * FROM user WHERE key='%s'" % key)
            s = self.cur.fetchone()
            self.conn.commit()
            return s
        except sqlite3.Error:
            raise

    def add_user(self, userinfo):
        """添加用户信息"""
        try:
            self.cur.execute(
                "INSERT INTO user(ip,key,priority,multiple,mark) \
                 VALUES(?,?,?,?,?)", userinfo)
            self.conn.commit()
        except sqlite3.Error:
            raise

    def end_of_cur(self):
        self.conn.commit()

    def sql_commit(self):
        self.conn.commit()

    def sql_rollback(self):
        self.conn.rollback()

if __name__ == "__main__":
    sl = RSqlite()
    # sl.create_table()
    serinfo = ('192.168.1.125', 8060, 'keytest', 10, 'mark')
    print sl.get_server_by_ip('192.168.1.125')

    del sl
