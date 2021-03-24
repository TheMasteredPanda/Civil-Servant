import mariadb

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

    #Closes the connection pool.
    def close(self):
        self.pool.close()

    '''
    A decorator used to execute queries and inject the result into the function. The decorator
    takes in the query that will be executed and the arguments passed to the function when
    the function is being called as the values to be placed into the query for all CRUD
    statements.

    @fetch("SELECT * FROM table_name WHERE id = ?")
    def test_function(result):
        ...

    test_function(1233322)
    
    Resulting query: SELECT * FROM table_name WHERE id = 1233322

    The result will then be injected into the function as 'result'
    '''
    def fetch(self, query: str):
        def decorator(*args, **kwargs):
            def wrapper(func):
                if query == '':
                    raise Exception('Query is empty')
            
                try:
                    pconn = self.pool.get_connection()
                    pcursor = pconn.cursor()
                    result = None

                    if len(args) == 0:
                        result = pcursor.execute(query)
                        
                    elif len(args) > 0:
                        result = pcursor.execute(query, args)

                    func(result) 
                    pconn.close()
                except mariadb.PoolError as ex:
                    raise ex
            return wrapper
        return decorator

    '''
    A function used to execute all CRUD operations. 
    The values parameter can either be a list of tuples or a tuple singularly

    If a result is not returned then a boolean is returned. True the statement executed 
    succesfully, otherwise FAlse
    '''
    def execute(self, *args, **kwargs): 
        try:
            pconn = self.pool.get_connection()
            pcursor = pconn.cursor()
            result = None

            if len(args) == 0 and len(kwargs) == 0:
                raise Exception("args and kwargs cannot be empty.")
            
            query: str = None

            if len(args) > 0:
                if isinstance(args[0], str) is False:
                    raise Exception("Query must be a string.")
                query = args[0].lower()
            else:
                if 'query' not in kwargs:
                    raise Exception("Keyword 'query' not found in kwargs.")
                if isinstance(args[0], str) is False:
                    raise Exception("Query must be a string.")

                query = kwargs['query'].lower()

            if query is None:
                raise Exception("query was null past the asssignment conditional statement. Should be impossible.")
        
            if 'values' in kwargs or len(args) >= 2:
                values = None

                if len(args) >= 2:
                    values = args[1]
                else:
                    values = kwargs['values']

                if isinstance(values, list) is False and isinstance(values, tuple) is False:
                    raise Exception("Values must be in either tuple or list[tuple]")

                if query.startswith('insert'):
                    if isinstance(values, list):
                        if len(values) == 0:
                            raise Exception('List is empty.')

                        tuple_irregularities = len(list(filter(lambda item: query.count('?') != len(item), values)))

                        if tuple_irregularities > 0:
                            raise Exception('Tuple length in a few entires is not equal to the query placeholder length. Query Length: {} Values: {}'.format(query.count('?'), tuple_irregularities))

                        result = pcursor.executemany(query, values)
                        if result is None: result = True
                    else:
                        if len(values) == 0:
                            raise Exception('Tuple is empty.')

                        if query.count('?') != len(values):
                            raise Exception('Tuple length is not equal to query placeholder length. Query Length: {} - Value Length: {} - Values: {}'.format(query.count('?'), len(values), values))
                        result = pcursor.execute(query, values)
                        if result is None: result = True
                        pcursor.close()
                        pconn.commit()
                else:
                    result = pcursor.execute(query, values)
                    if result is None: result = True
                    pcursor.close()
                    pconn.commit()
            else:
               pcursor.execute(query)
               result = True
               pcursor.close()
               pconn.commit()

            pconn.close()
            return result
        except mariadb.PoolError as ex:
            result = False
            raise ex
            return result
