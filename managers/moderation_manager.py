
class ModerationManager():
    def __init__(self, database):
        database.execute("CREATE TABLE IF NOT EXISTS punishment_logs(

