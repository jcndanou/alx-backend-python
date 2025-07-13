import sqlite3

class ExecuteQuery:
    def __init__(self, db_name, query, params=None):
        self.db_name = db_name
        self.query = query
        self.params = params or ()
        self.conn = None
        self.cursor = None

    def __enter__(self):
        # Ouvre la connexion et exécute la requête
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query, self.params)
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Ferme tout proprement
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

# Utilisation avec la requête demandée
with ExecuteQuery('users.db', "SELECT * FROM users WHERE age > ?", (25,)) as cursor:
    results = cursor.fetchall()
    for row in results:
        print(row)