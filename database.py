import mariadb
from mariadb import cursor, connection, ConnectionPool

#A manager for executing sql queries. 
class Database:
    def __init__(self, mariadb_config):
        username = mariadb_config['username']
        password = mariadb_config['password']
        host = mariadb_config['host']
        port = int(mariadb_config['port'])
        database = mariadb_config['database']
        pool_name = mariadb_config['connectionpoolname']
        pool_size = int(mariadb_config['connectionpoolsize'])

        print(pool_name)
        try:
            self.pool = mariadb.ConnectionPool(pool_name=pool_name, pool_size=pool_size, username=username, password=password, host=host, port=port, database=database)
        except mariadb.Error as ex:
            raise ex

    class Statement():
        def __init__(self, pool, first_values):
            self.table_name = None
            self.connection = pool.get_connection()
            self.cursor = self.connection.cursor()
            self.query = None
            self.values = None
            self.first_values = first_values
        
        def _build_statement(self):
            pass

        def get_cursor(self):
            return self.cursor

        def get_table_name(self):
            return self.table_name
        
        def execute(self):
            self._build_statement()

            try:
                self.cursor.execute(self.query, self.values)
                self.connection.commit()
            except connection.Error as err:
                pass


        def execute_many(self):
            self._build_statement()

            try:
                self.cursor.executemany(self.query, self.values)
                self.connection.commit()
            except connection.Error as err:
                pass


        def close(self):
            try:
                self.cursor.close()
                self.connection.close()
            except connection.Error as err:
                pass

    class FetchStatement(Statement):
        def __init__(self, pool):
            super().__init__(pool)
            self.conditionals = None

        def from(self, table_name: str):
            super().table_name = table_name

        def where(self, **kwargs):
            super().values = kwargs

        def _build_statement(self):
            super().query = "select {} from {} where {}".format(",".join(super().first_values), super().table_name, map(lambda kv: '{}={}'.format(kv[0], kv[1]), self.conditionals))

        def fetch(self, size: int):
            try:
                if size == 1: return super().cursor.fetchone()
                if size == -1: return super().cursor.fetchall()
                if size > 1: return super().cursor.fetchmany(size)
            except connection.Error as err:
                pass

    class InsertStatement(Statement):
        def __init__(self, pool, first_values):
            super().__init__(pool, first_values)
            self.into_columns = ()
        
        def into(self, table_name: str):
            super().table_name = table_name

        def columns(self, columns: tuple):
            self.into_columns = columns

        def _build_statement(self):
            super().query = "insert into {}{} values ?".format(super().table_name, '' if len(self.into_columns) == 0 else "({})".format(self.into_columns))
            super().values = super().first_values

    class UpdateStatement(Statement):
        def __init__(self, pool, first_values):
            super().__init__(pool, first_values)
            super().table_name = first_values
            self.set_values = {}

        def set(self, **kwargs):
            self.set_values = kwargs

        def where(self, **kwargs):
            super().values = kwargs

        def _build_statement(self):
            super().query = "update {} set {} where ?".format(super().table_name, ",".join(self.set_values))

    class DeleteStatement(Statement):
        def __init__(self, pool, first_values):
            super().__init__(pool, first_values)
            self.conditionals = {}

        def from(self, table_name):
            super().table_name = table_name

        def where(self, **kwargs):
            self.conditionals = kwargs

        def _build_statement(self):
            super().query = "delete from {} where {}".format(super().table_name, " and ".join(map(lambda kv: "{}={}".format(kv[0], kv[1]), self.conditionals)))
            
    #Closes the connection pool.
    def close(self):
        self.pool.close()

    def fetch(self, **kwargs):
        return self.FetchStatement(self.pool, kwargs)

    def insert(self, values: tuple or list(tuple)):
        return self.InsertStatement(self.pool, values)

    def update(self, table_name: str):
        return self.UpdateStatement(self, table_name)

    def delete(self):
        return self.DeleteStatement(self.pool, None)
