TABLE = 'disney'
TABLE_KEYS = ['movieid', 'title', 'year']

class Disney():
    def __init__ (self, session):
        self.session = session

    def GET_ALL(self):
        return self.session.GET_ALL(TABLE, TABLE_KEYS)

    def GET(self, id):
        return self.session.GET(TABLE, TABLE_KEYS, TABLE_KEYS[0], id)

    def POST(self, body_json):
        return self.session.POST(TABLE, TABLE_KEYS, body_json)

    def PUT(self, id, body_json):
        return self.session.PUT(TABLE, TABLE_KEYS, TABLE_KEYS[0], id, body_json)

    def DELETE(self, id):
        return self.session.DELETE(TABLE, TABLE_KEYS[0], id)
