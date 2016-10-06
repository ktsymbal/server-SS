import psycopg2
import json

DB = 'disneydb'
USER = 'disney'
PSWD = 'disneyforever'
TABLE = 'disney'
HOST = 'localhost'
TABLE_KEYS = ['movieid', 'title', 'year']

def GET_ALL():
    with psycopg2.connect(database=DB, user=USER, password=PSWD, host=HOST) as conn:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT * FROM {};".format(TABLE)
            )

            rows = cur.fetchall()
    if rows:
        return json.dumps([
            {TABLE_KEYS[0]:row[0], TABLE_KEYS[1]:row[1], TABLE_KEYS[2]:row[2]}
            for row in rows], indent=4, separators=(',', ': '))
    return None

def GET(id):
    with psycopg2.connect(database=DB, user=USER, password=PSWD, host=HOST) as conn:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT * FROM {} WHERE movieid = {};".format(TABLE, id)
            )

            row = cur.fetchone()
    if row:
        return json.dumps(
            {TABLE_KEYS[0]:row[0], TABLE_KEYS[1]:row[1], TABLE_KEYS[2]:row[2]},
            indent=4, separators=(',', ': '))
    return None

def POST(body_json):
    with psycopg2.connect(database=DB, user=USER, password=PSWD, host=HOST) as conn:
        with conn.cursor() as cur:
            try:
                if isinstance(body_json, list):
                    cur.executemany("""
                        INSERT INTO {0} ({1},{2})
                        VALUES (%({1})s, %({2})s)""".format(
                        TABLE, TABLE_KEYS[1], TABLE_KEYS[2]), body_json
                    )
                else:
                    cur.execute("""
                        INSERT INTO {0} ({1},{2})
                        VALUES (%({1})s, %({2})s)""".format(
                        TABLE, TABLE_KEYS[1], TABLE_KEYS[2]), body_json
                    )
                conn.commit()
            except psycopg2.DatabaseError:
                conn.rollback()
                raise

def PUT(body_json, rec_id):
    with psycopg2.connect(database=DB, user=USER, password=PSWD, host=HOST) as conn:
        with conn.cursor() as cur:
            try:
                set_values = ''
                for key in body_json.keys():
                    if not key in TABLE_KEYS:
                        raise psycopg2.DatabaseError('Wrong data format')
                    set_values += '{} = {}'.format(key, body_json[key])
                cur.execute("""
                    UPDATE {} SET {} WHERE movieid = {}""".format(TABLE, set_values, rec_id)
                )
                conn.commit()
            except psycopg2.DatabaseError:
                conn.rollback()
                raise

def DELETE (id):
    with psycopg2.connect(database=DB, user=USER, password=PSWD, host=HOST) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("""
                DELETE FROM {} WHERE movieid = {}""".format(TABLE, id)
            )
            except psycopg2.DatabaseError:
                conn.rollback()
                raise
