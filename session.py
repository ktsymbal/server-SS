import connection
import json
import psycopg2

class Session():
    def __init__(self):
        try:
            self.conn = connection.Connection()
            self.cur = self.conn.cursor()
        except psycopg2.Error, e:
            print e.pgerror

    def GET_ALL(self, table, table_keys):
        query = "SELECT * FROM {};".format(table)
        self.cur.execute(query)

        rows = self.cur.fetchall()
        if rows:
            return json.dumps([
                {table_keys[0]:row[0], table_keys[1]:row[1], table_keys[2]:row[2]}
                for row in rows], indent=4, separators=(',', ': '))
        return None

    def GET(self, table, table_keys, key, id):
        query = "SELECT * FROM {} WHERE {} = {};".format(table, key, id)
        self.cur.execute(query)
        row = self.cur.fetchone()
        if row:
            return json.dumps(
            {table_keys[0]:row[0], table_keys[1]:row[1], table_keys[2]:row[2]},
            indent=4, separators=(',', ': '))
        return None

    def POST(self, table, table_keys, body_json):
        try:
            if isinstance(body_json, list):
                query = "INSERT INTO {0} ({1},{2}) VALUES (%({1})s, %({2})s)".format(
                    table, table_keys[1], table_keys[2])
                self.cur.executemany(query, body_json)
            else:
                query = "INSERT INTO {0} ({1},{2}) VALUES (%({1})s, %({2})s)".format(
                    table, table_keys[1], table_keys[2])
                self.cur.execute(query, body_json)
            self.conn.commit()
        except psycopg2.DatabaseError:
            self.conn.rollback()
            raise

    def PUT(self, table, table_keys, key, id, body_json):
        try:
            set_values = ''
            for key_upd in body_json.keys():
                if not key_upd in table_keys:
                    raise psycopg2.DatabaseError('Wrong data format')
                if set_values:
                    set_values += ','
                set_values += '{0} = %({0})s'.format(key_upd)
            query = "UPDATE {0} SET {1} WHERE {2} = {3}".format(table, set_values, key, id)
            self.cur.execute(query, body_json)
            self.conn.commit()
        except psycopg2.DatabaseError:
            self.conn.rollback()
            raise

    def DELETE (self, table, key, id):
        try:
            query = "DELETE FROM {} WHERE {} = {}".format(table, key, id)
            self.cur.execute(query)
        except psycopg2.DatabaseError:
            self.conn.rollback()
            raise
