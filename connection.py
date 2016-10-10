import psycopg2

DB = 'disneydb'
USER = 'disney'
PSWD = 'disneyforever'
TABLE = 'disney'
HOST = 'localhost'

class Connection(object):

    __instance = None

    def __new__(cls):
        if cls.__instance == None:
            try:
                cls.__instance = psycopg2.connect(database=DB, user=USER, password=PSWD, host=HOST)
            except psycop2.Error, e:
                raise
        return cls.__instance

CONNECTION = None

def get_instance():
    if CONNECTION:
        return CONNECTION
    try:
        CONNECTION = psycopg2.connect(database=DB, user=USER, password=PSWD, host=HOST)
    except psycop2.Error, e:
        raise
